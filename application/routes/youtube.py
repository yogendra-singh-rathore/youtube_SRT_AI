from application import app
from application.config.db_conn import get_db_connection
from flask import render_template, request, redirect, url_for, jsonify, Blueprint

yt = Blueprint('youtube', __name__)

@yt.route('/youtube', methods=['GET', 'POST'])
def youtube():
    with get_db_connection() as conn:
        cursor = conn.cursor()

        if request.method == 'POST':
            video_id = request.form.get('video_id')
            video_title = request.form.get('video_title')
            video_url = request.form.get('video_url')
            video_description = request.form.get('video_description')
            video_status = request.form.get('video_status')
            subtitle_languages = request.form.getlist('subtitle_languages')
            new_language = request.form.get('new_language')
            playlist_name = request.form.get('playlist_name')
            new_playlist = request.form.get('new_playlist')
            playlist_status = request.form.get('playlist_status')
            end_video_1 = request.form.get('end_video_1')
            end_video_2 = request.form.get('end_video_2')

            print(f"Playlist Status: {playlist_status}")  # Debug statement

            if new_language:
                cursor.execute('SELECT id FROM subtitle_language_table WHERE language = ?', (new_language,))
                if not cursor.fetchone():
                    cursor.execute('INSERT INTO subtitle_language_table (language) VALUES (?)', (new_language,))
                subtitle_languages.append(new_language)

            if new_playlist:
                cursor.execute('SELECT id FROM playlist_table WHERE playlist_name = ?', (new_playlist,))
                if not cursor.fetchone():
                    cursor.execute('INSERT INTO playlist_table (playlist_name) VALUES (?)', (new_playlist,))
                playlist_name = new_playlist

            # Editing existing video
            if video_id:
                cursor.execute('''
                    UPDATE video_table SET video_title = ?, video_url = ?, video_description = ? WHERE id = ?
                ''', (video_title, video_url, video_description, video_id))

                cursor.execute('DELETE FROM video_status WHERE video_id = ?', (video_id,))
                cursor.execute('''
                    INSERT INTO video_status (video_id, status_id) 
                    VALUES (?, (SELECT id FROM status_table WHERE status = ?))
                ''', (video_id, video_status))

                cursor.execute('DELETE FROM videoLanguage_table WHERE video_id = ?', (video_id,))
                for language in subtitle_languages:
                    cursor.execute('''
                        INSERT INTO videoLanguage_table (video_id, subtitle_id) 
                        VALUES (?, (SELECT id FROM subtitle_language_table WHERE language = ?))
                    ''', (video_id, language))

                cursor.execute('DELETE FROM video_playlist_table WHERE video_id = ?', (video_id,))
                if playlist_name:
                    cursor.execute('''
                        INSERT INTO video_playlist_table (video_id, playlist_id) 
                        VALUES (?, (SELECT id FROM playlist_table WHERE playlist_name = ?))
                    ''', (video_id, playlist_name))

                cursor.execute('''
                    UPDATE end_video_table SET end_video_1_id = ?, end_video_2_id = ? 
                    WHERE video_id = ?
                ''', (end_video_1 if end_video_1 != 'None' else None, end_video_2 if end_video_2 != 'None' else None, video_id))

                # Update playlist status for the specific playlist associated with the current video
                if playlist_name:
                    cursor.execute('DELETE FROM playlist_status WHERE playlist_id = (SELECT id FROM playlist_table WHERE playlist_name = ?) AND EXISTS (SELECT 1 FROM video_playlist_table WHERE video_id = ?)', (playlist_name, video_id))
                    cursor.execute('''
                        INSERT INTO playlist_status (playlist_id, status_id) 
                        VALUES ((SELECT id FROM playlist_table WHERE playlist_name = ?), (SELECT id FROM status_table WHERE status = ?))
                    ''', (playlist_name, playlist_status))
            else:  # Adding new video
                cursor.execute('''
                    INSERT INTO video_table (video_title, video_url, video_description) 
                    VALUES (?, ?, ?)
                ''', (video_title, video_url, video_description))
                video_id = cursor.lastrowid

                cursor.execute('''
                    INSERT INTO video_status (video_id, status_id) 
                    VALUES (?, (SELECT id FROM status_table WHERE status = ?))
                ''', (video_id, video_status))

                for language in subtitle_languages:
                    cursor.execute('''
                        INSERT INTO videoLanguage_table (video_id, subtitle_id) 
                        VALUES (?, (SELECT id FROM subtitle_language_table WHERE language = ?))
                    ''', (video_id, language))

                if playlist_name:
                    cursor.execute('''
                        INSERT INTO video_playlist_table (video_id, playlist_id) 
                        VALUES (?, (SELECT id FROM playlist_table WHERE playlist_name = ?))
                    ''', (video_id, playlist_name))

                    cursor.execute('''
                        INSERT INTO playlist_status (playlist_id, status_id) 
                        VALUES ((SELECT id FROM playlist_table WHERE playlist_name = ?), (SELECT id FROM status_table WHERE status = ?))
                    ''', (playlist_name, playlist_status))

                cursor.execute('''
                    INSERT INTO end_video_table (video_id, end_video_1_id, end_video_2_id) 
                    VALUES (?, ?, ?)
                ''', (video_id, end_video_1 if end_video_1 != 'None' else None, end_video_2 if end_video_2 != 'None' else None))


            conn.commit()
            return redirect(url_for('youtube.youtube'))

        search_query = request.args.get('search', '')
        status_filter = request.args.get('status', '')
        page = int(request.args.get('page', 1))
        rows_per_page = 10
        offset = (page - 1) * rows_per_page

        query = '''
            WITH subtitles AS (
                SELECT video_id, GROUP_CONCAT(language, ', ') AS subtitle_languages
                FROM videoLanguage_table vl
                JOIN subtitle_language_table slt ON vl.subtitle_id = slt.id
                GROUP BY video_id
            )
            SELECT vt.id, vt.video_title, vt.video_url, vt.video_description,
                st.status as video_status,
                COALESCE(sub.subtitle_languages, '') as subtitle_languages,
                ev1.video_title as end_video_1,
                ev2.video_title as end_video_2,
                pt.playlist_name,
                pst.status as playlist_status
            FROM video_table vt
            LEFT JOIN video_status vs ON vt.id = vs.video_id
            LEFT JOIN status_table st ON vs.status_id = st.id
            LEFT JOIN subtitles sub ON vt.id = sub.video_id
            LEFT JOIN end_video_table evt ON vt.id = evt.video_id
            LEFT JOIN video_table ev1 ON evt.end_video_1_id = ev1.id
            LEFT JOIN video_table ev2 ON evt.end_video_2_id = ev2.id
            LEFT JOIN video_playlist_table vp ON vt.id = vp.video_id
            LEFT JOIN playlist_table pt ON vp.playlist_id = pt.id
            LEFT JOIN playlist_status ps ON pt.id = ps.playlist_id
            LEFT JOIN status_table pst ON ps.status_id = pst.id
            WHERE (vt.video_title LIKE ? OR vt.video_description LIKE ?)
            AND (st.status = ? OR ? = '')
            GROUP BY vt.id, pt.playlist_name  -- Ensure grouping by playlist name as well
            LIMIT ? OFFSET ?
        '''
        videos = cursor.execute(query, (f'%{search_query}%', f'%{search_query}%', status_filter, status_filter, rows_per_page, offset)).fetchall()


        total_query = '''
            SELECT COUNT(*)
            FROM video_table vt
            LEFT JOIN video_status vs ON vt.id = vs.video_id
            LEFT JOIN status_table st ON vs.status_id = st.id
            WHERE (vt.video_title LIKE ? OR vt.video_description LIKE ?)
            AND (st.status = ? OR ? = '')
        '''
        total_count = cursor.execute(total_query, (f'%{search_query}%', f'%{search_query}%', status_filter, status_filter)).fetchone()[0]
        total_pages = (total_count + rows_per_page - 1) // rows_per_page

        subtitle_languages = cursor.execute('SELECT language FROM subtitle_language_table').fetchall()
        playlists = cursor.execute('SELECT playlist_name FROM playlist_table').fetchall()
        statuses = cursor.execute('SELECT status FROM status_table').fetchall()

    return render_template('youtube.html', videos=videos, subtitle_languages=[lang['language'] for lang in subtitle_languages],
                           playlists=[playlist['playlist_name'] for playlist in playlists], statuses=[status['status'] for status in statuses],
                           search_query=search_query, status_filter=status_filter, current_page=page, total_pages=total_pages)

@yt.route('/edit_video/<int:video_id>', methods=['GET'])
def edit_video(video_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        video = cursor.execute('''
            WITH subtitles AS (
                SELECT video_id, GROUP_CONCAT(language, ', ') AS subtitle_languages
                FROM videoLanguage_table vl
                JOIN subtitle_language_table slt ON vl.subtitle_id = slt.id
                GROUP BY video_id
            )
            SELECT vt.id, vt.video_title, vt.video_url, vt.video_description,
                   st.status as video_status,
                   COALESCE(sub.subtitle_languages, '') as subtitle_languages,
                   evt.end_video_1_id, evt.end_video_2_id,
                   pt.playlist_name,
                   pst.status as playlist_status
            FROM video_table vt
            LEFT JOIN video_status vs ON vt.id = vs.video_id
            LEFT JOIN status_table st ON vs.status_id = st.id
            LEFT JOIN subtitles sub ON vt.id = sub.video_id
            LEFT JOIN end_video_table evt ON vt.id = evt.video_id
            LEFT JOIN video_playlist_table vp ON vt.id = vp.video_id
            LEFT JOIN playlist_table pt ON vp.playlist_id = pt.id
            LEFT JOIN playlist_status ps ON pt.id = ps.playlist_id
            LEFT JOIN status_table pst ON ps.status_id = pst.id
            WHERE vt.id = ?
            GROUP BY vt.id
        ''', (video_id,)).fetchone()

    return jsonify({
        'id': video['id'],
        'video_title': video['video_title'],
        'video_url': video['video_url'],
        'video_description': video['video_description'],
        'video_status': video['video_status'],
        'subtitle_languages': video['subtitle_languages'].split(', ') if video['subtitle_languages'] else [],
        'end_video_1_id': video['end_video_1_id'],
        'end_video_2_id': video['end_video_2_id'],
        'playlist_name': video['playlist_name'],
        'playlist_status': video['playlist_status']
    })
