from flask import Blueprint, render_template, request, session, redirect, url_for, flash, Response
from datetime import datetime, timedelta
import csv
import io
from src.database.database import connect_db
from src.utils.decorators import login_required

management_bp = Blueprint('management', __name__)


# --- Bulk import helpers -----------------------------------------------------

# Accept a few common header spellings for each column.
_COLUMN_ALIASES = {
    'class': {'class', 'class_name', 'classname', 'grade', 'section', 'batch'},
    'subject': {'subject', 'subject_name', 'subjectname', 'course', 'paper'},
    'teacher': {'teacher', 'teacher_name', 'teachername', 'faculty', 'instructor'},
    'semester': {'semester', 'sem', 'term'},
    'credits': {'credits', 'credit', 'weekly_lectures', 'lectures', 'periods'},
}


def _map_headers(header_row):
    """Map a spreadsheet header row to our canonical field names."""
    mapping = {}
    for idx, raw in enumerate(header_row):
        key = str(raw or '').strip().lower().replace(' ', '_')
        for field, aliases in _COLUMN_ALIASES.items():
            if key in aliases:
                mapping[field] = idx
                break
    return mapping


def _rows_from_upload(file_storage):
    """Return a list of raw rows (each a list of cell values) from a csv/xlsx/ods upload."""
    filename = (file_storage.filename or '').lower()
    data = file_storage.read()

    if filename.endswith('.csv') or filename.endswith('.txt'):
        text = data.decode('utf-8-sig', errors='replace')
        return [row for row in csv.reader(io.StringIO(text))]

    if filename.endswith('.xlsx'):
        try:
            import openpyxl
        except ImportError:
            raise ValueError("Excel support is not installed on the server.")
        wb = openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True)
        ws = wb.active
        return [[c for c in row] for row in ws.iter_rows(values_only=True)]

    raise ValueError("Unsupported file type. Please upload a .csv or .xlsx file.")


def _parse_curriculum(file_storage):
    """Parse an upload into a list of {class, subject, teacher, semester, credits} dicts."""
    rows = [r for r in _rows_from_upload(file_storage) if r and any(
        str(c).strip() for c in r if c is not None)]
    if not rows:
        raise ValueError("The file appears to be empty.")

    headers = _map_headers(rows[0])
    if 'class' not in headers or 'subject' not in headers or 'teacher' not in headers:
        raise ValueError(
            "Missing required columns. The first row must contain headers for "
            "Class, Subject and Teacher (Semester and Credits are optional).")

    records = []
    for row in rows[1:]:
        def cell(field):
            i = headers.get(field)
            if i is None or i >= len(row) or row[i] is None:
                return ''
            return str(row[i]).strip()

        class_name = cell('class')
        subject = cell('subject')
        teacher = cell('teacher')
        if not (class_name and subject and teacher):
            continue

        def to_int(field, default):
            val = cell(field)
            try:
                return int(float(val)) if val else default
            except (ValueError, TypeError):
                return default

        records.append({
            'class': class_name,
            'subject': subject,
            'teacher': teacher,
            'semester': to_int('semester', 1),
            'credits': to_int('credits', 4),
        })
    return records


@management_bp.route('/import_curriculum', methods=['POST'])
@login_required
def import_curriculum():
    school_id = session['school_id']
    file = request.files.get('curriculum_file')
    if not file or not file.filename:
        flash('Please choose a file to import.', 'error')
        return redirect(url_for('management.manage_subjects'))

    try:
        records = _parse_curriculum(file)
    except Exception as e:
        flash(f'Import failed: {e}', 'error')
        return redirect(url_for('management.manage_subjects'))

    if not records:
        flash('No valid rows found in the file.', 'error')
        return redirect(url_for('management.manage_subjects'))

    db = connect_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Ensure a course exists (subjects reference one).
        cursor.execute("SELECT course_id FROM course WHERE school_id = %s LIMIT 1", (school_id,))
        course = cursor.fetchone()
        if not course:
            cursor.execute("INSERT INTO course (course_name, school_id) VALUES ('Standard', %s)", (school_id,))
            course_id = cursor.lastrowid
        else:
            course_id = course['course_id']

        # Cache existing classes/teachers so we reuse instead of duplicating.
        cursor.execute("SELECT class_id, class_name FROM class WHERE school_id = %s", (school_id,))
        class_map = {r['class_name'].strip().lower(): r['class_id'] for r in cursor.fetchall()}
        cursor.execute("SELECT teacher_id, teacher_name FROM teacher WHERE school_id = %s", (school_id,))
        teacher_map = {r['teacher_name'].strip().lower(): r['teacher_id'] for r in cursor.fetchall()}

        classes_added = teachers_added = subjects_added = 0

        for rec in records:
            ckey = rec['class'].lower()
            if ckey not in class_map:
                cursor.execute("INSERT INTO class (class_name, school_id) VALUES (%s, %s)", (rec['class'], school_id))
                class_map[ckey] = cursor.lastrowid
                classes_added += 1

            tkey = rec['teacher'].lower()
            if tkey not in teacher_map:
                cursor.execute("INSERT INTO teacher (teacher_name, school_id) VALUES (%s, %s)", (rec['teacher'], school_id))
                teacher_map[tkey] = cursor.lastrowid
                teachers_added += 1

            cursor.execute("""
                INSERT INTO subject (subject_name, class_id, course_id, teacher_id, semester, credits, school_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (rec['subject'], class_map[ckey], course_id, teacher_map[tkey],
                  rec['semester'], rec['credits'], school_id))
            subjects_added += 1

        db.commit()
        flash(
            f'Import successful: added {subjects_added} subjects, '
            f'{classes_added} new classes and {teachers_added} new teachers.',
            'success')
    except Exception as e:
        db.rollback()
        flash(f'Import failed while saving: {e}', 'error')
    finally:
        db.close()

    return redirect(url_for('management.manage_subjects'))


@management_bp.route('/sample_curriculum.csv')
@login_required
def sample_curriculum():
    """A ready-to-fill template so users know the expected columns."""
    sample = (
        "Class,Subject,Teacher,Semester,Credits\n"
        "10th Grade A,Mathematics,John Doe,1,5\n"
        "10th Grade A,Physics,Jane Smith,1,4\n"
        "10th Grade B,Mathematics,John Doe,1,5\n"
    )
    return Response(
        sample,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=curriculum_template.csv'})

@management_bp.route('/manage_teachers', methods=['GET', 'POST'])
@login_required
def manage_teachers():
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    edit_teacher = None
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'delete':
            teacher_id = request.form.get('teacher_id')
            try:
                cursor.execute("DELETE FROM timetable WHERE teacher_id = %s AND school_id = %s", (teacher_id, session['school_id']))
                cursor.execute("DELETE FROM allocated_timeslots WHERE teacher_id = %s AND school_id = %s", (teacher_id, session['school_id']))
                cursor.execute("DELETE FROM subject WHERE teacher_id = %s AND school_id = %s", (teacher_id, session['school_id']))
                cursor.execute("DELETE FROM teacher WHERE teacher_id = %s AND school_id = %s", (teacher_id, session['school_id']))
                db.commit()
                flash('Teacher and their assigned subjects deleted successfully!', 'success')
            except Exception as e:
                flash(f'Error deleting teacher: {str(e)}', 'error')
        elif action == 'update':
            teacher_id = request.form.get('teacher_id')
            name = request.form.get('teacher_name')
            try:
                cursor.execute("UPDATE teacher SET teacher_name = %s WHERE teacher_id = %s AND school_id = %s", (name, teacher_id, session['school_id']))
                db.commit()
                flash('Teacher updated successfully!', 'success')
                return redirect(url_for('management.manage_teachers'))
            except Exception as e:
                flash(f'Error updating teacher: {str(e)}', 'error')
        else:
            try:
                name = request.form.get('teacher_name')
                if name:
                    cursor.execute("INSERT INTO teacher (teacher_name, school_id) VALUES (%s, %s)", (name, session['school_id']))
                    db.commit()
                    flash('Teacher added successfully!', 'success')
            except Exception as e:
                flash(f'Error adding teacher: {str(e)}', 'error')

    edit_id = request.args.get('edit_id')
    if edit_id:
        cursor.execute("SELECT * FROM teacher WHERE teacher_id = %s AND school_id = %s", (edit_id, session['school_id']))
        edit_teacher = cursor.fetchone()
            
    cursor.execute("SELECT * FROM teacher WHERE school_id = %s", (session['school_id'],))
    teachers = cursor.fetchall()
    db.close()
    return render_template('manage_teachers.html', teachers=teachers, edit_teacher=edit_teacher)

@management_bp.route('/manage_subjects', methods=['GET', 'POST'])
@login_required
def manage_subjects():
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    school_id = session['school_id']

    cursor.execute("SELECT course_id FROM course WHERE school_id = %s LIMIT 1", (school_id,))
    course = cursor.fetchone()
    if not course:
        cursor.execute("INSERT INTO course (course_name, school_id) VALUES ('Standard', %s)", (school_id,))
        db.commit()
        course_id = cursor.lastrowid
    else:
        course_id = course['course_id']
        
    edit_class = None
    edit_subject = None

    if request.method == 'POST':
        action = request.form.get('action')
        try:
            if action == 'add_class':
                class_name = request.form.get('class_name')
                if class_name:
                    cursor.execute("INSERT INTO class (class_name, school_id) VALUES (%s, %s)", (class_name, school_id))
                    db.commit()
                    flash('Class added successfully!', 'success')
            elif action == 'update_class':
                class_id = request.form.get('class_id')
                class_name = request.form.get('class_name')
                cursor.execute("UPDATE class SET class_name = %s WHERE class_id = %s AND school_id = %s", (class_name, class_id, school_id))
                db.commit()
                flash('Class updated successfully!', 'success')
                return redirect(url_for('management.manage_subjects'))
            elif action == 'delete_class':
                class_id = request.form.get('class_id')
                cursor.execute("DELETE FROM subject WHERE class_id = %s AND school_id = %s", (class_id, school_id))
                cursor.execute("DELETE FROM class WHERE class_id = %s AND school_id = %s", (class_id, school_id))
                db.commit()
                flash('Class and its subjects deleted successfully!', 'success')
            elif action == 'add_subject':
                subject_name = request.form.get('subject_name')
                class_id = request.form.get('class_id')
                teacher_id = request.form.get('teacher_id')
                # Schools don't expose semester/credits in the form, so fall back
                # to sensible defaults (semester 1, 4 weekly periods).
                credits = request.form.get('credits') or 4
                semester = request.form.get('semester') or 1
                cursor.execute("""
                    INSERT INTO subject (subject_name, class_id, course_id, teacher_id, semester, credits, school_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (subject_name, class_id, course_id, teacher_id, semester, credits, school_id))
                db.commit()
                flash('Subject added successfully!', 'success')
            elif action == 'update_subject':
                subject_id = request.form.get('subject_id')
                subject_name = request.form.get('subject_name')
                class_id = request.form.get('class_id')
                teacher_id = request.form.get('teacher_id')
                credits = request.form.get('credits') or 4
                semester = request.form.get('semester') or 1
                cursor.execute("""
                    UPDATE subject SET subject_name=%s, class_id=%s, teacher_id=%s, semester=%s, credits=%s
                    WHERE subject_id=%s AND school_id=%s
                """, (subject_name, class_id, teacher_id, semester, credits, subject_id, school_id))
                db.commit()
                flash('Subject updated successfully!', 'success')
                return redirect(url_for('management.manage_subjects'))
            elif action == 'delete_subject':
                subject_id = request.form.get('subject_id')
                cursor.execute("DELETE FROM subject WHERE subject_id = %s AND school_id = %s", (subject_id, school_id))
                db.commit()
                flash('Subject deleted successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    edit_class_id = request.args.get('edit_class_id')
    if edit_class_id:
        cursor.execute("SELECT * FROM class WHERE class_id = %s AND school_id = %s", (edit_class_id, school_id))
        edit_class = cursor.fetchone()
    edit_subject_id = request.args.get('edit_subject_id')
    if edit_subject_id:
         cursor.execute("SELECT * FROM subject WHERE subject_id = %s AND school_id = %s", (edit_subject_id, school_id))
         edit_subject = cursor.fetchone()

    cursor.execute("SELECT * FROM class WHERE school_id = %s", (school_id,))
    classes = cursor.fetchall()
    cursor.execute("SELECT * FROM teacher WHERE school_id = %s", (school_id,))
    teachers = cursor.fetchall()
    cursor.execute("""
        SELECT s.*, c.class_name, t.teacher_name 
        FROM subject s
        JOIN class c ON s.class_id = c.class_id
        JOIN teacher t ON s.teacher_id = t.teacher_id
        WHERE s.school_id = %s
    """, (school_id,))
    subjects = cursor.fetchall()
    db.close()
    return render_template('manage_subjects.html', classes=classes, teachers=teachers, subjects=subjects, edit_class=edit_class, edit_subject=edit_subject)

@management_bp.route('/manage_timings', methods=['GET', 'POST'])
@login_required
def manage_timings():
    if request.method == 'POST':
        start_time_str = request.form.get('start_time')
        lecture_duration = int(request.form.get('lecture_duration'))
        num_lectures = int(request.form.get('num_lectures'))
        break_after = int(request.form.get('break_after'))
        break_duration = int(request.form.get('break_duration') or 0)

        start_time = datetime.strptime(start_time_str, "%H:%M")
        break_start_time = None
        break_start_str = None
        if break_after > 0:
            break_start_time = start_time + timedelta(minutes=break_after * lecture_duration)
            break_start_str = break_start_time.strftime("%H:%M")
        
        total_minutes = num_lectures * lecture_duration
        if break_after > 0 and break_after < num_lectures:
             total_minutes += break_duration
        end_time = start_time + timedelta(minutes=total_minutes)
        end_time_str = end_time.strftime("%H:%M")

        db = connect_db()
        cursor = db.cursor()
        try:
            sql = """
                UPDATE schools SET start_time = %s, end_time = %s, lecture_duration = %s, break_start_time = %s, break_duration = %s
                WHERE school_id = %s
            """
            cursor.execute(sql, (start_time_str, end_time_str, lecture_duration, break_start_str, break_duration, session['school_id']))
            db.commit()
            session['time_config'] = {
                'start_time': start_time_str, 'end_time': end_time_str, 'lecture_duration': lecture_duration,
                'break_start': break_start_str, 'break_duration': break_duration,
                'num_lectures': num_lectures, 'break_after': break_after
            }
            flash('Timings updated successfully!', 'success')
        except Exception as e:
            flash(f'Error updating timings: {str(e)}', 'error')
        finally:
            db.close()
        return redirect(url_for('management.manage_timings'))

    config = session.get('time_config')
    if config and 'num_lectures' not in config:
        try:
            s_time = datetime.strptime(config.get('start_time'), "%H:%M")
            e_time = datetime.strptime(config.get('end_time'), "%H:%M")
            l_dur = int(config.get('lecture_duration', 60))
            b_dur = int(config.get('break_duration', 0))
            b_start_str = config.get('break_start')
            total_duration = (e_time - s_time).seconds / 60
            if b_start_str:
                b_start = datetime.strptime(b_start_str, "%H:%M")
                lectures_before = (b_start - s_time).seconds / 60 / l_dur
                b_end = b_start + timedelta(minutes=b_dur)
                lectures_after = (e_time - b_end).seconds / 60 / l_dur
                config['num_lectures'] = int(lectures_before + lectures_after)
                config['break_after'] = int(lectures_before)
            else:
                config['num_lectures'] = int(total_duration / l_dur)
                config['break_after'] = 0
        except Exception: pass
    return render_template('manage_timings.html', config=config)
