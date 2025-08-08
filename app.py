from flask import Flask, render_template, request, redirect
import psycopg2

app = Flask(__name__)

# Configuración de conexión a PostgreSQL
conn = psycopg2.connect(
    dbname="",
    user="",
    password="",
    host=",
    port=""

)

cursor = conn.cursor()

@app.route('/sirecq_interno', methods=['GET', 'POST'])
def sirecq_interno():
    if request.method == 'POST':
        no_requerimiento = request.form.get('no_requerimiento')
        descripcion = request.form.get('descripcion')
        tramitePR = request.form.get('tramitePR') or None
        seguimientoInst = request.form.get('seguimientoInst') or None
        id_dependencia = request.form.get('id_dependencia') or None
        id_sistema = request.form.get('id_sistema') or None
        id_categoria = request.form['id_categoria'] or None
        tramiteCat = request.form.get('tramiteCat') or None
        id_rol_usuario = request.form.get('id_rol_usuario') or None  # Responsable
        fecha_registro = request.form.get('fecha_registro') or None
        oficioEnvioDmi = request.form.get('oficioEnvioDmi') or None
        fechaEnvioReq = request.form.get('fechaEnvioReq') or None
        ofi_desp_pt = request.form.get('ofi_desp_pt') or None
        fech_desp_pt = request.form.get('fech_desp_pt') or None
        id_estado = request.form.get('id_estado') or None
        observacionesGen = request.form.get('observacionesGen') or None
        obsv_tecnica = request.form.get('obsv_tecnica') or None
        tecnico_id = request.form.get('tecnico') or None
        fase= request.form.get('fase') or 'Requisito'  
        num_version = request.form.get('num_version') 
        clasif_id = request.form.get('clasif') or None
        prioridad = request.form.get('prioridad') or None
        fecha_env_dmc = request.form.get('fecha_env_dmc') or None
        tema = request.form.get('tema') or None
        documento = request.form.get('documento') or None
        usuario_registra = request.form.get('usuario_registra') or None      



        # Insertar en versionamiento
        cursor.execute("""
            INSERT INTO versionamiento (oficioEnvioDmi, fechaEnvioReq, ofi_desp_pt, fech_desp_pt, num_version)
            VALUES (%s, %s, %s, %s, %s) RETURNING id_version
        """, (oficioEnvioDmi, fechaEnvioReq, ofi_desp_pt, fech_desp_pt, num_version))
        id_versionamiento = cursor.fetchone()[0]

        

        # Insertar en requerimiento (sin id_versionamiento)
        cursor.execute("""
            INSERT INTO requerimiento (
                id_estado_requerimiento, id_rol_usuario,
                id_sistema, id_categoria, no_requerimiento,
                fecha_registro, documento, tema, descripcion, fase
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_requerimiento
        """, (
            id_estado, id_rol_usuario, id_sistema, id_categoria,
            no_requerimiento, fecha_registro, documento, tema, descripcion, fase
        ))
        id_requerimiento = cursor.fetchone()[0]

        # Insertar relación requerimiento-versionamiento
        cursor.execute("""
            INSERT INTO requerimiento_version (id_requerimiento, id_version)
            VALUES (%s, %s)
        """, (id_requerimiento, id_versionamiento))

        # Insertar en sirecq_externo
        cursor.execute("""
            INSERT INTO sirecq_externo (
                id_requerimiento, id_dependencia, tramitePR, seguimientoInst, tramiteCat, observacionesGen
            ) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_sirecq_externo
        """, (id_requerimiento, id_dependencia, tramitePR, seguimientoInst, tramiteCat, observacionesGen))
        id_sirecq_externo = cursor.fetchone()[0]

        # Insertar en sirecq_interno
        cursor.execute("""
            INSERT INTO sirecq_interno (
                id_sirecq_externo, prioridad, id_clasif_catastral, fecha_env_dmc, obsv_tecnica
            ) VALUES (%s, %s, %s, %s, %s) RETURNING id_sirecq_interno
        """, (id_sirecq_externo, prioridad, clasif_id, fecha_env_dmc, obsv_tecnica))
        id_sirecq_interno = cursor.fetchone()[0]  # <--- AQUÍ capturas el ID

        # Insertar en usuario_sirecq (asignar técnico)
        cursor.execute("""
            INSERT INTO usuario_sirecq (id_rol_usuario, id_sirecq_interno)
            VALUES (%s, %s)
        """, (tecnico_id, id_sirecq_interno))

        conn.commit()
        return redirect('/sirecq_interno')

    # GET - cargar selects
    cursor.execute("SELECT id_dependencia, nombre_dependencia FROM dependencia")
    dependencias = cursor.fetchall()

# Cargar categorías
    cursor.execute("SELECT id_categoria, nom_categoria FROM categoria")
    categorias = cursor.fetchall()

    cursor.execute("SELECT id_estado_requerimiento, nombre_estado_requerimiento FROM estado_requerimiento")
    estados = cursor.fetchall()
    
    cursor.execute("""
        SELECT ru.id_rol_usuario, u.nombre_usuario || ' ' || u.apellidos_usuario
        FROM rol_usuario ru
        JOIN usuario u ON ru.id_usuario = u.id_usuario
    """)
    usuarios = cursor.fetchall()


    cursor.execute("""
        SELECT ru.id_rol_usuario, u.nombre_usuario || ' ' || u.apellidos_usuario
        FROM rol_usuario ru
        JOIN usuario u ON ru.id_usuario = u.id_usuario
        JOIN rol r ON ru.id_rol = r.id_rol
        WHERE r.nombre_rol ILIKE '%ejecutor%'
    """)
    responsables = cursor.fetchall()

    cursor.execute("""
        SELECT ru.id_rol_usuario, u.nombre_usuario || ' ' || u.apellidos_usuario
        FROM rol_usuario ru
        JOIN usuario u ON ru.id_usuario = u.id_usuario
        JOIN rol r ON ru.id_rol = r.id_rol
        WHERE r.nombre_rol ILIKE '%técnico%'
    """)
    tecnicos = cursor.fetchall()

    cursor.execute("SELECT id_sistema, nom_sistema FROM sistema")
    sistemas = cursor.fetchall()

    cursor.execute("SELECT id_clasif_catastral, nombre_clasif_catastral FROM clasif_catastral")
    clasificaciones = cursor.fetchall()

   

    return render_template(
    'sirecq_interno.html',
    dependencias=dependencias,
    estados=estados,
    responsables=responsables,
    tecnicos=tecnicos,
    usuarios=usuarios,
    sistemas=sistemas,
    clasificaciones=clasificaciones,
    categorias=categorias  
)




@app.route('/sirecq_externo', methods=['GET', 'POST'])
def sirecq_externo():
    if request.method == 'POST':
        no_requerimiento = request.form.get('no_requerimiento')
        descripcion = request.form.get('descripcion')

        # Validación obligatoria
        if not no_requerimiento or not descripcion:
            return "Faltan campos obligatorios: número de requerimiento o descripción", 400

        # Campos opcionales
        tramitePR = request.form.get('tramitePR') or None
        seguimientoInst = request.form.get('seguimientoInst') or None
        id_dependencia = request.form.get('id_dependencia') or None
        id_sistema = request.form.get('id_sistema') or None
        id_categoria = request.form.get('id_categoria') or None
        tramiteCat = request.form.get('tramiteCat') or None
        fase = request.form.get('fase') or None
        id_rol_usuario = request.form.get('id_rol_usuario') or None
        fecha_registro = request.form.get('fecha_registro') or None
        oficioEnvioDmi = request.form.get('oficioEnvioDmi') or None
        fechaEnvioReq = request.form.get('fechaEnvioReq') or None
        ofi_desp_pt = request.form.get('ofi_desp_pt') or None
        fech_desp_pt = request.form.get('fech_desp_pt') or None
        num_version = request.form.get('num_version') or None
        id_estado = request.form.get('id_estado') or None
        observacionesGen = request.form.get('observacionesGen') or None

        # Insertar en versionamiento
        cursor.execute("""
            INSERT INTO versionamiento (oficioEnvioDmi, fechaEnvioReq, ofi_desp_pt, fech_desp_pt, num_version)
            VALUES (%s, %s, %s, %s, %s) RETURNING id_version
        """, (oficioEnvioDmi, fechaEnvioReq, ofi_desp_pt, fech_desp_pt, num_version))
        id_versionamiento = cursor.fetchone()[0]

        # Insertar en requerimiento
        cursor.execute("""
            INSERT INTO requerimiento (
                id_estado_requerimiento, id_rol_usuario,
                id_sistema, id_categoria, no_requerimiento,
                fecha_registro, descripcion, fase
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_requerimiento
        """, (
            id_estado, id_rol_usuario, id_sistema, id_categoria,
            no_requerimiento, fecha_registro, descripcion, fase
        ))
        id_requerimiento = cursor.fetchone()[0]

        # Relación requerimiento-versionamiento
        cursor.execute("""
            INSERT INTO requerimiento_version (id_requerimiento, id_version)
            VALUES (%s, %s)
        """, (id_requerimiento, id_versionamiento))

        # Insertar en sirecq_externo
        cursor.execute("""
            INSERT INTO sirecq_externo (
                id_requerimiento, id_dependencia, tramitePR,
                seguimientoInst, tramiteCat, observacionesGen
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            id_requerimiento, id_dependencia, tramitePR,
            seguimientoInst, tramiteCat, observacionesGen
        ))

        conn.commit()
        return redirect('/sirecq_externo')

    # GET - Selects
    cursor.execute("SELECT id_dependencia, nombre_dependencia FROM dependencia")
    dependencias = cursor.fetchall()

    cursor.execute("SELECT id_estado_requerimiento, nombre_estado_requerimiento FROM estado_requerimiento")
    estados = cursor.fetchall()

    cursor.execute("""
        SELECT ru.id_rol_usuario, u.nombre_usuario || ' ' || u.apellidos_usuario
        FROM rol_usuario ru
        JOIN usuario u ON ru.id_usuario = u.id_usuario
        JOIN rol r ON ru.id_rol = r.id_rol
        WHERE r.nombre_rol ILIKE '%ejecutor%'
    """)
    ejecutores = cursor.fetchall()

    cursor.execute("SELECT id_sistema, nom_sistema FROM sistema")
    sistemas = cursor.fetchall()

    cursor.execute("SELECT id_categoria, nom_categoria FROM categoria")
    categorias = cursor.fetchall()

    return render_template(
        'sirecq_externo.html',
        dependencias=dependencias,
        estados=estados,
        responsables=ejecutores,
        sistemas=sistemas,
        categorias=categorias
    )



@app.route('/test_produccion', methods=['GET', 'POST'])
def test_produccion():
    if request.method == 'POST':
        # Requerimiento
        no_requerimiento = request.form.get('no_requerimiento')
        descripcion = request.form.get('descripcion')
        id_estado = request.form.get('id_estado') or None
        id_rol_usuario = request.form.get('id_rol_usuario') or None
        id_categoria = request.form.get('id_categoria') or None
        id_sistema = request.form.get('id_sistema') or None
        fase = request.form.get('fase') or None

        # Versionamiento
        oficioEnvioDmi = request.form.get('oficioEnvioDmi') or None
        fechaEnvioReq = request.form.get('fechaEnvioReq') or None
        ofi_desp_pt = request.form.get('ofi_desp_pt') or None
        fech_desp_pt = request.form.get('fech_desp_pt') or None
        num_version = request.form.get('num_version') 

        # Test Producción
        etapa_implementacion = request.form.get('etapa_implementacion')
        respuesta_tics = request.form.get('respuesta_tics') or None

        # Validación obligatorios
        if not no_requerimiento or not descripcion:
            return "El número de requerimiento y la descripción son obligatorios.", 400

        # Insertar en versionamiento
        cursor.execute("""
            INSERT INTO versionamiento (oficioEnvioDmi, fechaEnvioReq, ofi_desp_pt, fech_desp_pt, num_version)
            VALUES (%s, %s, %s, %s) RETURNING id_version
        """, (oficioEnvioDmi, fechaEnvioReq, ofi_desp_pt, fech_desp_pt, num_version))
        id_version = cursor.fetchone()[0]

        # Insertar en requerimiento
        cursor.execute("""
            INSERT INTO requerimiento (
                id_estado_requerimiento, id_rol_usuario, id_categoria, id_sistema,
                no_requerimiento, descripcion, fase
            ) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_requerimiento
        """, (id_estado, id_rol_usuario, id_categoria, id_sistema,
              no_requerimiento, descripcion, fase))
        id_requerimiento = cursor.fetchone()[0]

        # Insertar en requerimiento_version
        cursor.execute("""
            INSERT INTO requerimiento_version (id_requerimiento, id_version)
            VALUES (%s, %s)
        """, (id_requerimiento, id_version))

        # Insertar en test_produccion
        cursor.execute("""
            INSERT INTO test_produccion (
                id_requerimiento, id_rol_usuario, etapa_implementacion, respuesta_tics
            ) VALUES (%s, %s, %s, %s)
        """, (id_requerimiento, id_rol_usuario, etapa_implementacion, respuesta_tics))

        conn.commit()
        return redirect('/test_produccion')

    # GET - Cargar selects
    cursor.execute("SELECT id_estado_requerimiento, nombre_estado_requerimiento FROM estado_requerimiento")
    estados = cursor.fetchall()

    cursor.execute("""
        SELECT ru.id_rol_usuario, u.nombre_usuario || ' ' || u.apellidos_usuario
        FROM rol_usuario ru
        JOIN usuario u ON ru.id_usuario = u.id_usuario
        JOIN rol r ON ru.id_rol = r.id_rol
        WHERE r.nombre_rol ILIKE '%ejecutor%'
    """)
    ejecutores = cursor.fetchall()

    cursor.execute("SELECT id_categoria, nom_categoria FROM categoria")
    categorias = cursor.fetchall()

    cursor.execute("SELECT id_sistema, nom_sistema FROM sistema")
    sistemas = cursor.fetchall()

    return render_template('test_produccion.html',
                           estados=estados,
                           ejecutores=ejecutores,
                           categorias=categorias,
                           sistemas=sistemas)

if __name__ == '__main__':
    app.run(debug=True)
