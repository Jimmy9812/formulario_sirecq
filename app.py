from flask import Flask, render_template, request, redirect
import psycopg2

app = Flask(__name__)

# Configuración de conexión a PostgreSQL
conn = psycopg2.connect(
    dbname="CatastroDB_P2",
    user="postgres",
    password="12345",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

@app.route('/', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        no_requerimiento = request.form['no_requerimiento']
        descripcion = request.form['descripcion']
        prioridad_id = request.form['prioridad']
        clasif_id = request.form['clasif']
        tramitePR = request.form['tramitePR']
        seguimientoInst = request.form['seguimientoInst']
        dependencia_id = request.form['dependencia']
        sistema_afectar = request.form['sistema_afectar']
        tramiteCat = request.form['tramiteCat']
        responsable_id = request.form['responsable']
        tecnico_id = request.form['tecnico']
        fecha_env_dmc = request.form['fecha_env_dmc']
        oficio_envio = request.form['oficio_envio']
        fecha_envio_req = request.form['fecha_envio_req']
        oficio_despacho = request.form['oficio_despacho']
        fecha_desp_pt = request.form['fecha_desp_pt']
        estado_id = request.form['estado']
        observacionesGen = request.form['observacionesGen']
        obsv_tecnica = request.form['obsv_tecnica']

        # Insertar en versionamiento
        cursor.execute("""
            INSERT INTO versionamiento (oficioEnvioDmi, fechaEnvioReq, ofi_desp_pt, fecha_desp_pt)
            VALUES (%s, %s, %s, %s) RETURNING id_version
        """, (oficio_envio, fecha_envio_req, oficio_despacho, fecha_desp_pt))
        version_id = cursor.fetchone()[0]

        # Insertar en requerimiento
        cursor.execute("""
            INSERT INTO requerimiento (id_estado_requerimiento, id_versionamiento, no_requerimiento,
                fecha_registro, documento, tema, descripcion, sistema_afectar, categoria)
            VALUES (%s, %s, %s, CURRENT_DATE, 'doc.pdf', 'tema', %s, %s, 'Tecnología') RETURNING id_requerimiento
        """, (estado_id, version_id, no_requerimiento, descripcion, sistema_afectar))
        req_id = cursor.fetchone()[0]

        # Insertar en test_produccion
        cursor.execute("""
            INSERT INTO test_produccion (id_requerimiento, id_rol_usuario, etapa_implementacion, respuesta_tics)
            VALUES (%s, %s, 'N/A', 'N/A') RETURNING id_test_produccion
        """, (req_id, tecnico_id))

        # Insertar en sirecq_externo
        cursor.execute("""
            INSERT INTO sirecq_externo (id_requerimiento, id_dependencia, tramitePR, seguimientoInst, tramiteCat, observacionesGen)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_sirecq_externo
        """, (req_id, dependencia_id, tramitePR, seguimientoInst, tramiteCat, observacionesGen))
        sirecq_ext_id = cursor.fetchone()[0]

        # Insertar en sirecq_interno
        cursor.execute("""
            INSERT INTO sirecq_interno (id_sirecq_externo, id_prioridad, id_clasif_catastral, fecha_env_dmc, obsv_tecnica)
            VALUES (%s, %s, %s, %s, %s) RETURNING id_sirecq_interno
        """, (sirecq_ext_id, prioridad_id, clasif_id, fecha_env_dmc, obsv_tecnica))
        sirecq_int_id = cursor.fetchone()[0]

        # Insertar en usuario_sirecq
        cursor.execute("""
            INSERT INTO usuario_sirecq (id_rol_usuario, id_sirecq_interno)
            VALUES (%s, %s)
        """, (responsable_id, sirecq_int_id))

        conn.commit()
        return redirect('/')

    # Obtener listas para selects (nombre e id)
    cursor.execute("SELECT ru.id_rol_usuario, u.nombre_usuario || ' ' || u.apellidos_usuario AS nombre_responsable FROM rol_usuario ru INNER JOIN rol r ON ru.id_rol = r.id_rol INNER JOIN usuario u ON ru.id_usuario = u.id_usuario WHERE r.nombre_rol ILIKE '%responsable%';")
    responsables = cursor.fetchall()
    cursor.execute("SELECT ru.id_rol_usuario, u.nombre_usuario || ' ' || u.apellidos_usuario AS nombre_tecnico FROM rol_usuario ru INNER JOIN rol r ON ru.id_rol = r.id_rol INNER JOIN usuario u ON ru.id_usuario = u.id_usuario WHERE r.nombre_rol ILIKE '%técnico%'")
    tecnicos = cursor.fetchall()
    cursor.execute("SELECT id_dependencia, nombre_dependencia FROM dependencia")
    dependencias = cursor.fetchall()
    cursor.execute("SELECT id_prioridad, nombre_prioridad FROM prioridad")
    prioridades = cursor.fetchall()
    cursor.execute("SELECT id_clasif_catastral, nombre_clasif_catastral FROM clasif_catastral")
    clasificaciones = cursor.fetchall()
    cursor.execute("SELECT id_estado_requerimiento, nombre_estado_requerimiento FROM estado_requerimiento")
    estados = cursor.fetchall()

    return render_template('formulario.html', responsables=responsables, tecnicos=tecnicos,
                           dependencias=dependencias, prioridades=prioridades,
                           clasificaciones=clasificaciones, estados=estados)

if __name__ == '__main__':
    app.run(debug=True)
