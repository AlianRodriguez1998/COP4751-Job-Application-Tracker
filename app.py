"""COP4751 Job Application Tracker — Flask routes, validation, dashboard and CRUD."""
import json
import os
import secrets
from datetime import date
from hmac import compare_digest
from urllib.parse import urlparse

from dotenv import load_dotenv
from flask import (Flask, abort, flash, redirect, render_template, request,
                   session, url_for)
from mysql.connector import Error, IntegrityError

import database
from matching import rank_jobs, skills_from_text

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY') or secrets.token_hex(32)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024

# Field definitions are the only source of dynamic SQL identifiers; no user-controlled
# table or column name is interpolated into a query.
ENTITIES = {
    'companies': {
        'pk': 'company_id', 'singular': 'Company', 'title': 'Companies',
        'fields': [
            ('company_name', 'Company name', 'text', True, 100),
            ('industry', 'Industry', 'text', False, 50),
            ('website', 'Website', 'url', False, 200),
            ('city', 'City', 'text', False, 50),
            ('state', 'State', 'text', False, 50),
            ('notes', 'Notes', 'textarea', False, None),
        ],
        'list_fields': ('company_name', 'industry', 'city', 'state'),
    },
    'jobs': {
        'pk': 'job_id', 'singular': 'Job', 'title': 'Jobs',
        'fields': [
            ('company_id', 'Company', 'company_select', True, None),
            ('job_title', 'Job title', 'text', True, 100),
            ('job_type', 'Job type', 'job_type', False, None),
            ('salary_min', 'Minimum salary ($)', 'nonnegative_int', False, None),
            ('salary_max', 'Maximum salary ($)', 'nonnegative_int', False, None),
            ('job_url', 'Job posting URL', 'url', False, 300),
            ('date_posted', 'Date posted', 'date', False, None),
            ('requirements', 'Required skills (comma-separated)', 'skills', False, None),
        ],
        'list_fields': ('job_title', 'company_name', 'job_type', 'date_posted'),
    },
    'applications': {
        'pk': 'application_id', 'singular': 'Application', 'title': 'Applications',
        'fields': [
            ('job_id', 'Job', 'job_select', True, None),
            ('application_date', 'Application date', 'date', True, None),
            ('status', 'Status', 'status', False, None),
            ('resume_version', 'Resume version', 'text', False, 50),
            ('cover_letter_sent', 'Cover letter sent', 'checkbox', False, None),
            ('interview_data', 'Interview data (JSON object or array)', 'json', False, None),
        ],
        'list_fields': ('job_title', 'company_name', 'application_date', 'status'),
    },
    'contacts': {
        'pk': 'contact_id', 'singular': 'Contact', 'title': 'Contacts',
        'fields': [
            ('company_id', 'Company', 'company_select', True, None),
            ('contact_name', 'Contact name', 'text', True, 100),
            ('title', 'Title', 'text', False, 100),
            ('email', 'Email', 'email', False, 100),
            ('phone', 'Phone', 'text', False, 20),
            ('linkedin_url', 'LinkedIn URL', 'url', False, 200),
            ('notes', 'Notes', 'textarea', False, None),
        ],
        'list_fields': ('contact_name', 'company_name', 'title', 'email'),
    },
}
JOB_TYPES = ['Full-time', 'Part-time', 'Contract', 'Internship']
STATUSES = ['Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn']


def csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_urlsafe(32)
    return session['_csrf_token']


app.jinja_env.globals['csrf_token'] = csrf_token


@app.before_request
def verify_csrf():
    if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
        provided = request.form.get('_csrf_token', '')
        if not compare_digest(str(provided), str(session.get('_csrf_token', ''))):
            abort(400, 'Invalid form token. Reload the page and try again.')


@app.context_processor
def template_globals():
    return {'entities': ENTITIES, 'job_types': JOB_TYPES, 'statuses': STATUSES,
            'today': date.today().isoformat()}


def select_sql(entity):
    if entity == 'jobs':
        return ('SELECT jobs.*, companies.company_name FROM jobs '
                'JOIN companies ON jobs.company_id = companies.company_id')
    if entity == 'applications':
        return ('SELECT applications.*, jobs.job_title, companies.company_name '
                'FROM applications JOIN jobs ON applications.job_id = jobs.job_id '
                'JOIN companies ON jobs.company_id = companies.company_id')
    if entity == 'contacts':
        return ('SELECT contacts.*, companies.company_name FROM contacts '
                'JOIN companies ON contacts.company_id = companies.company_id')
    return 'SELECT * FROM companies'


def foreign_options(entity):
    if entity in ('jobs', 'contacts'):
        return database.query('SELECT company_id AS id, company_name AS label '
                              'FROM companies ORDER BY company_name')
    if entity == 'applications':
        return database.query('SELECT jobs.job_id AS id, '
                              'CONCAT(jobs.job_title, " — ", companies.company_name) AS label '
                              'FROM jobs JOIN companies ON jobs.company_id = companies.company_id '
                              'ORDER BY companies.company_name, jobs.job_title')
    return []


def validate_form(entity, form):
    """Return validated database values and human-readable field errors."""
    values = {}
    errors = {}
    for key, label, kind, required, max_len in ENTITIES[entity]['fields']:
        raw = (form.get(key, '') or '').strip()
        if kind == 'checkbox':
            values[key] = 1 if form.get(key) == 'on' else 0
            continue
        if required and not raw:
            errors[key] = f'{label} is required.'
            continue
        if max_len and len(raw) > max_len:
            errors[key] = f'{label} must be at most {max_len} characters.'
            continue
        if not raw:
            values[key] = None
            continue
        if kind in ('company_select', 'job_select'):
            if not raw.isdecimal() or int(raw) < 1:
                errors[key] = f'Select a valid {label.lower()}.'
            else:
                values[key] = int(raw)
        elif kind == 'nonnegative_int':
            try:
                number = int(raw)
                if not 0 <= number <= 2147483647:
                    raise ValueError
                values[key] = number
            except ValueError:
                errors[key] = f'{label} must be a nonnegative whole number.'
        elif kind == 'date':
            try:
                values[key] = date.fromisoformat(raw)
            except ValueError:
                errors[key] = f'{label} must be a valid YYYY-MM-DD date.'
        elif kind == 'job_type':
            if raw not in JOB_TYPES:
                errors[key] = 'Select a valid job type.'
            else:
                values[key] = raw
        elif kind == 'status':
            if raw not in STATUSES:
                errors[key] = 'Select a valid status.'
            else:
                values[key] = raw
        elif kind == 'skills':
            skills = skills_from_text(raw)
            if any(len(s) > 100 for s in skills) or len(skills) > 100:
                errors[key] = 'Enter at most 100 skills, each at most 100 characters.'
            else:
                values[key] = json.dumps(skills)
        elif kind == 'json':
            try:
                data = json.loads(raw)
                if not isinstance(data, (dict, list)):
                    raise ValueError
                values[key] = json.dumps(data)
            except (ValueError, TypeError):
                errors[key] = 'Enter a valid JSON object or array, e.g. {"round": 1}.'
        elif kind == 'email':
            if '@' not in raw or '.' not in raw.rsplit('@', 1)[-1] or ' ' in raw:
                errors[key] = 'Enter a valid email address.'
            else:
                values[key] = raw
        elif kind == 'url':
            parsed = urlparse(raw)
            if parsed.scheme not in ('http', 'https') or not parsed.netloc:
                errors[key] = 'Enter a full http:// or https:// URL.'
            else:
                values[key] = raw
        else:
            values[key] = raw
    if entity == 'jobs':
        lo, hi = values.get('salary_min'), values.get('salary_max')
        if lo is not None and hi is not None and lo > hi:
            errors['salary_max'] = 'Maximum salary must not be lower than minimum salary.'
    return values, errors


def form_data_from_row(entity, row):
    data = {}
    for key, _, kind, _, _ in ENTITIES[entity]['fields']:
        value = row.get(key)
        if value is None:
            data[key] = ''
        elif kind == 'skills':
            from matching import requirement_skills
            data[key] = ', '.join(requirement_skills(value))
        elif kind == 'json':
            data[key] = json.dumps(json.loads(value) if isinstance(value, str) else value,
                                   indent=2, default=str)
        elif kind == 'date':
            data[key] = value.isoformat() if hasattr(value, 'isoformat') else str(value)
        else:
            data[key] = value
    return data


@app.route('/')
def dashboard():
    counts = {
        'companies': database.query('SELECT COUNT(*) AS n FROM companies', one=True)['n'],
        'jobs': database.query('SELECT COUNT(*) AS n FROM jobs', one=True)['n'],
        'applications': database.query('SELECT COUNT(*) AS n FROM applications', one=True)['n'],
        'contacts': database.query('SELECT COUNT(*) AS n FROM contacts', one=True)['n'],
    }
    status_counts = database.query('SELECT status, COUNT(*) AS n FROM applications '
                                   'GROUP BY status ORDER BY n DESC')
    recent = database.query(select_sql('applications') +
                            ' ORDER BY application_date DESC, application_id DESC LIMIT 6')
    return render_template('dashboard.html', counts=counts, status_counts=status_counts,
                           recent=recent)


@app.route('/<entity>')
def entity_list(entity):
    if entity not in ENTITIES:
        abort(404)
    pk = ENTITIES[entity]['pk']
    rows = database.query(select_sql(entity) + f' ORDER BY {pk} DESC')
    return render_template(f'{entity}.html', entity=entity, meta=ENTITIES[entity], rows=rows)


@app.route('/<entity>/new', methods=['GET', 'POST'])
def entity_new(entity):
    if entity not in ENTITIES:
        abort(404)
    data, errors = {}, {}
    if request.method == 'POST':
        data = request.form.to_dict()
        values, errors = validate_form(entity, request.form)
        if not errors:
            fields = list(values)
            cols = ', '.join(fields)
            placeholders = ', '.join(['%s'] * len(fields))
            try:
                database.execute(f'INSERT INTO {entity} ({cols}) VALUES ({placeholders})',
                                 tuple(values.values()))
                flash(f'{ENTITIES[entity]["singular"]} created successfully.', 'success')
                return redirect(url_for('entity_list', entity=entity))
            except IntegrityError:
                errors['_general'] = 'The selected company or job does not exist.'
    return render_template('entity_form.html', entity=entity, meta=ENTITIES[entity],
                           data=data, errors=errors, options=foreign_options(entity), editing=False)


@app.route('/<entity>/<int:record_id>')
def entity_detail(entity, record_id):
    if entity not in ENTITIES:
        abort(404)
    pk = ENTITIES[entity]['pk']
    row = database.query(select_sql(entity) + f' WHERE {entity}.{pk} = %s',
                         (record_id,), one=True)
    if row is None:
        abort(404)
    return render_template('entity_detail.html', entity=entity,
                           meta=ENTITIES[entity], record=row)


@app.route('/<entity>/<int:record_id>/edit', methods=['GET', 'POST'])
def entity_edit(entity, record_id):
    if entity not in ENTITIES:
        abort(404)
    pk = ENTITIES[entity]['pk']
    row = database.query(f'SELECT * FROM {entity} WHERE {pk} = %s', (record_id,), one=True)
    if row is None:
        abort(404)
    data, errors = form_data_from_row(entity, row), {}
    if request.method == 'POST':
        data = request.form.to_dict()
        values, errors = validate_form(entity, request.form)
        if not errors:
            updates = ', '.join(f'{column} = %s' for column in values)
            try:
                database.execute(f'UPDATE {entity} SET {updates} WHERE {pk} = %s',
                                 (*values.values(), record_id))
                flash(f'{ENTITIES[entity]["singular"]} updated successfully.', 'success')
                return redirect(url_for('entity_list', entity=entity))
            except IntegrityError:
                errors['_general'] = 'The selected company or job does not exist.'
    return render_template('entity_form.html', entity=entity, meta=ENTITIES[entity],
                           data=data, errors=errors, options=foreign_options(entity),
                           editing=True, record_id=record_id)


@app.route('/<entity>/<int:record_id>/delete', methods=['POST'])
def entity_delete(entity, record_id):
    if entity not in ENTITIES:
        abort(404)
    pk = ENTITIES[entity]['pk']
    try:
        affected = database.execute(f'DELETE FROM {entity} WHERE {pk} = %s', (record_id,))
        if affected:
            flash(f'{ENTITIES[entity]["singular"]} deleted.', 'success')
        else:
            flash('Record not found.', 'error')
    except IntegrityError:
        flash('Cannot delete this record while related records exist. Delete related '
              'applications, jobs or contacts first.', 'error')
    return redirect(url_for('entity_list', entity=entity))


@app.route('/job-match', methods=['GET', 'POST'])
def job_match():
    raw = ''
    jobs = []
    entered = False
    skills = []
    if request.method == 'POST':
        entered = True
        raw = request.form.get('skills', '')[:2000]
        skills = skills_from_text(raw)
        if not skills:
            flash('Enter at least one skill separated by commas.', 'error')
        else:
            jobs = rank_jobs(database.query(select_sql('jobs') + ' ORDER BY jobs.job_title'), skills)
    return render_template('job_match.html', raw=raw, jobs=jobs, entered=entered, skills=skills)


@app.errorhandler(400)
@app.errorhandler(404)
def client_error(err):
    return render_template('error.html', message=err.description, code=err.code), err.code


@app.errorhandler(Error)
def db_error(err):
    app.logger.exception('Database failure: %s', err)
    return render_template('error.html', code=503,
                           message='Database is unavailable. Check MySQL and the .env settings.'), 503


if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG') == '1')
