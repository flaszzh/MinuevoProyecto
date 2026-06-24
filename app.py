from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "cafearoma2026"

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
    producto = db.Column(db.String(100))
    total = db.Column(db.Float)


@app.route("/productos")
def productos():
    productos = Producto.query.all()

    resultado = ""

    for producto in productos:
        resultado += f"{producto.id} - {producto.nombre} - S/{producto.precio}<br>"

    return resultado


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form["usuario"]
        password = request.form["password"]

        if usuario == "admin" and password == "1234":

            session["admin"] = True

            return redirect("/dashboard")

        return "Usuario o contraseña incorrectos"

    return render_template("login.html")

@app.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect("/")

@app.route("/dashboard")
def dashboard():

    if not session.get("admin"):
        return redirect("/login")

    productos = Producto.query.all()
    pedidos = Pedido.query.all()
    ultimos_pedidos = Pedido.query.order_by(
    Pedido.id.desc()
).limit(5).all()

    total_productos = len(productos)
    total_pedidos = len(pedidos)

    ventas_totales = sum(
        pedido.total for pedido in pedidos
        if pedido.total is not None
    )

    meta_mensual = 500

    porcentaje_meta = round(
    (ventas_totales / meta_mensual) * 100,
    1
) if meta_mensual > 0 else 0

    if total_pedidos > 0:
        ticket_promedio = round(
            ventas_totales / total_pedidos,
            2
        )
    else:
        ticket_promedio = 0

    return render_template (
        "dashboard.html",
        productos=productos,
        total=total_productos,
        total_pedidos=total_pedidos,
        ventas_totales=ventas_totales,
        ticket_promedio=ticket_promedio,
        meta_mensual=meta_mensual,
        porcentaje_meta=porcentaje_meta,
        ultimos_pedidos=ultimos_pedidos
    )

@app.route("/pedidos")
def pedidos():

    if not session.get("admin"):
        return redirect("/login")

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

    datos_producto = request.form["producto"]

    producto, precio = datos_producto.split("|")

    nuevo_pedido = Pedido(
        nombre=request.form["nombre"],
        direccion=request.form["direccion"],
        celular=request.form["celular"],
        metodo_pago=request.form["pago"],
        producto=producto,
        total=float(precio)
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