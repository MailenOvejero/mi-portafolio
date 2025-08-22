from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import psycopg2.extras
import bcrypt
from werkzeug.utils import secure_filename
import os
from config import db_config

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'static/img'


# ===============================
# Ruta principal: muestra proyectos + perfil
# ===============================
@app.route('/')
def index():
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


    # proyectoos
    cursor.execute("SELECT * FROM proyectos")
    proyectos = cursor.fetchall()
    for p in proyectos:
        p['titulo'] = p['nombre']

    # fotoPerfil
    cursor.execute("SELECT * FROM perfil LIMIT 1")
    perfil = cursor.fetchone()

    conn.close()

    return render_template('index.html', proyectos=proyectos, perfil=perfil)


# ===============================
# Login
# ===============================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']

        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT * FROM usuarios WHERE usuario=%s", (usuario,))
        usuario_db = cursor.fetchone()
        conn.close()

        if usuario_db and bcrypt.checkpw(contraseña.encode('utf-8'), usuario_db['contraseña'].encode('utf-8')):
            session['usuario'] = usuario
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error='Usuario o contraseña incorrectos')

    return render_template('login.html')


# ===============================
# Logout
# ===============================
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))


# ===============================
# Panel admin protegido
# ===============================
@app.route('/admin')
def admin():
    if 'usuario' in session:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


        # proyects
        cursor.execute("SELECT * FROM proyectos")
        proyectos = cursor.fetchall()
        for p in proyectos:
            p['titulo'] = p['nombre']

        # perfill
        cursor.execute("SELECT * FROM perfil LIMIT 1")
        perfil = cursor.fetchone()

        conn.close()
        return render_template('admin.html', proyectos=proyectos, perfil=perfil)
    else:
        return redirect(url_for('login'))


# ===============================
# Agregar proyecto
# ===============================
@app.route('/agregar_proyecto', methods=['POST'])
def agregar_proyecto():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    titulo = request.form['titulo'].strip()
    descripcion = request.form['descripcion'].strip()
    imagen = request.files['imagen']
    link = request.form.get('link', '').strip()

    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


    # valido titulovacio
    if not titulo:
        cursor.execute("SELECT * FROM proyectos")
        proyectos = cursor.fetchall()
        conn.close()

        for p in proyectos:
            p['titulo'] = p['nombre']

        return render_template('admin.html', proyectos=proyectos, error='El título no puede estar vacío')

    # valido si el nombre est duplicado
    cursor.execute("SELECT * FROM proyectos WHERE nombre = %s", (titulo,))
    existente = cursor.fetchone()

    if existente:
        cursor.execute("SELECT * FROM proyectos")
        proyectos = cursor.fetchall()
        conn.close()

        for p in proyectos:
            p['titulo'] = p['nombre']

        return render_template('admin.html', proyectos=proyectos, error='Ya existe un proyecto con ese título')

    # guardo la imagen y registo proyecto
    if imagen and imagen.filename != '':
        nombre_archivo = secure_filename(imagen.filename)
        ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo)
        imagen.save(ruta_imagen)

        cursor.execute(
            "INSERT INTO proyectos (nombre, descripcion, imagen, link) VALUES (%s, %s, %s, %s)",
            (titulo, descripcion, f'img/{nombre_archivo}', link)
        )
        conn.commit()

    conn.close()
    return redirect(url_for('admin'))


# ===============================
# Eliminar proyecto
# ===============================
@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_proyecto(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT imagen FROM proyectos WHERE id = %s", (id,))
    resultado = cursor.fetchone()
    if resultado:
        imagen = resultado['imagen']
        ruta = os.path.join(app.root_path, 'static', imagen)
        if os.path.exists(ruta):
            os.remove(ruta)

    cursor.execute("DELETE FROM proyectos WHERE id = %s", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('admin'))


# ===============================
# Ver CV
# ===============================
@app.route('/cv')
def cv():
    return render_template('cv.html')


# ===============================
# Subir/editar foto de perfil
# ===============================
@app.route('/editar_perfil', methods=['POST'])
def editar_perfil():
    if 'imagen' not in request.files:
        return redirect(url_for('admin'))

    archivo = request.files['imagen']

    if archivo and archivo.filename != '':
        filename = secure_filename(archivo.filename)
        ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        archivo.save(ruta)

        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


        # Buco la img actual
        cursor.execute("SELECT imagen FROM perfil LIMIT 1")
        actual = cursor.fetchone()

        # borro la img ant. solo si existe y no es string vacio
        if actual and actual[0]:
            ruta_vieja = os.path.join('static', actual[0])
            if os.path.exists(ruta_vieja):
                os.remove(ruta_vieja)

        # Guardar la nueva en la base
        cursor.execute("UPDATE perfil SET imagen = %s", (f"img/{filename}",))
        conn.commit()
        conn.close()

    return redirect(url_for('admin'))


# ===============================
# Eliminar foto de perfil
# ===============================
@app.route('/eliminar_perfil', methods=['POST'])
def eliminar_perfil():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("SELECT imagen FROM perfil WHERE id = 1")
    actual = cursor.fetchone()
    if actual and os.path.exists(os.path.join('static', actual['imagen'])):
        os.remove(os.path.join('static', actual['imagen']))

    cursor.execute("UPDATE perfil SET imagen = '' WHERE id = 1")
    conn.commit()
    conn.close()

    return redirect(url_for('admin'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
