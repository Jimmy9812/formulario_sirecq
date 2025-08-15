from flask import Flask, request, redirect, render_template
import psycopg2

app = Flask(__name__)

# Conexión
conn = psycopg2.connect(
    dbname="catastrodb_p2",
    user="karol",
    password="Karol2510@Masoquista",
    host="ep-icy-waterfall-ad8hxp3v-pooler.c-2.us-east-1.aws.neon.tech",
    port="5432"
)
cursor = conn.cursor()

@app.route('/subir_imagen', methods=['GET', 'POST'])
def subir_imagen():
    if request.method == 'POST':
        id_incidente = request.form['id_incidente']
        error_img = request.files['imagen']

        if error_img:
            imagen_bytes = error_img.read()
            cursor.execute("""
                UPDATE incidente
                SET error_img = %s
                WHERE id_incidente = %s
            """, (imagen_bytes, id_incidente))
            conn.commit()
            return "Imagen subida exitosamente."

    return render_template('subir_imagen.html')

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/imagen/<int:id_incidente>')
def ver_imagen(id_incidente):
    cursor.execute("SELECT error_img FROM incidente WHERE id_incidente = %s", (id_incidente,))
    resultado = cursor.fetchone()
    if resultado and resultado[0]:
        return send_file(io.BytesIO(resultado[0]), mimetype='image/jpeg')
    else:
        return "Imagen no encontrada o incidente sin imagen", 404
