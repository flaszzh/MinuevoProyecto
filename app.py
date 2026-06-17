from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuración de SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafeteria.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Tabla Productos
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    celular = db.Column(db.String(20))
    metodo_pago = db.Column(db.String(50))

@app.route("/productos")
def productos():
    productos = Producto.query.all()

    resultado = ""

    for producto in productos:
        resultado += f"{producto.id} - {producto.nombre} - S/{producto.precio}<br>"

    return resultado

@app.route("/dashboard")
def dashboard():
    productos = Producto.query.all()

    return render_template(
        "dashboard.html",
        productos=productos,
        total=len(productos)
    )

@app.route("/pedidos")
def pedidos():

    pedidos = Pedido.query.all()

    return render_template(
        "pedidos.html",
        pedidos=pedidos
    )

@app.route("/agregar", methods=["GET", "POST"])
def agregar():

    if request.method == "POST":

        nombre = request.form["nombre"]
        precio = request.form["precio"]

        nuevo_producto = Producto(
            nombre=nombre,
            precio=precio
        )

        db.session.add(nuevo_producto)
        db.session.commit()

        return redirect("/dashboard")

    return render_template("agregar.html")

@app.route("/eliminar/<int:id>")
def eliminar(id):

    producto = Producto.query.get_or_404(id)

    db.session.delete(producto)
    db.session.commit()

    return redirect("/dashboard")

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):

    producto = Producto.query.get_or_404(id)

    if request.method == "POST":

        producto.nombre = request.form["nombre"]
        producto.precio = request.form["precio"]

        db.session.commit()

        return redirect("/dashboard")

    return render_template(
        "editar.html",
        producto=producto
    )

@app.route("/limpiar")
def limpiar():
    Producto.query.delete()
    db.session.commit()
    return "Base de datos limpiada"

@app.route("/cargar-productos")
def cargar_productos():

    productos = [
        Producto(nombre="Café Americano", precio=8),
        Producto(nombre="Capuccino", precio=10),
        Producto(nombre="Cheesecake", precio=12),
        Producto(nombre="Crema Volteada", precio=9),
        Producto(nombre="Tiramisú", precio=14),
        Producto(nombre="Croissant de Jamón y Queso", precio=7),
        Producto(nombre="Caramel Latte", precio=13),
        Producto(nombre="Matcha Latte", precio=15)
    ]

    for producto in productos:
        db.session.add(producto)

    db.session.commit()

    return "Productos cargados correctamente"

@app.route("/pedido", methods=["POST"])
def pedido():

    nuevo_pedido = Pedido(
        nombre=request.form["nombre"],
        direccion=request.form["direccion"],
        celular=request.form["celular"],
        metodo_pago=request.form["pago"]
    )

    db.session.add(nuevo_pedido)
    db.session.commit()

    return """
    <h1>Pedido registrado correctamente ☕</h1>

    <p>Gracias por tu compra.</p>

    <a href="/">Volver a Café Aroma</a>
    """

@app.route("/")
def inicio():
    return render_template("index.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)