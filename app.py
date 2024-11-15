import tkinter as tk
from tkinter import messagebox, ttk
from pyzbar.pyzbar import decode
import cv2
import psycopg2

# Función para conectar con la base de datos PostgreSQL
def conectar_db():
    return psycopg2.connect(
        dbname="inventory_db",  # Nombre de la base de datos
        user=".......",       # Nombre de usuario de PostgreSQL
        password=".......",  # Tu contraseña de PostgreSQL
        host="localhost",       # Dirección del servidor
        port="5432"             # Puerto de PostgreSQL
    )

# Crear la ventana principal
root = tk.Tk()
root.title("Gestión de Inventario")
root.geometry("600x500")  # Tamaño de la ventana
root.config(bg="#f5f5f5")  # Fondo claro

# Fuente personalizada
fuente = ("Arial", 12)

# Estilo ttk para personalizar los widgets
style = ttk.Style()
style.configure("TButton", padding=6, relief="flat", background="#4CAF50", font=("Arial", 12))
style.configure("TLabel", background="#f5f5f5", font=("Arial", 12))
style.configure("TEntry", padding=5, font=("Arial", 12), relief="solid")

# Crear frames para organizar los widgets
frame_entrada = tk.Frame(root, bg="#f5f5f5")
frame_entrada.pack(pady=10)

frame_botones = tk.Frame(root, bg="#f5f5f5")
frame_botones.pack(pady=20)

# Etiquetas y campos de entrada para código de barras, nombre y cantidad
etiqueta_codigo_barras = ttk.Label(frame_entrada, text="Código de barras:")
etiqueta_codigo_barras.grid(row=0, column=0, padx=10, pady=5, sticky="e")

entrada_codigo_barras = ttk.Entry(frame_entrada, width=20)
entrada_codigo_barras.grid(row=0, column=1, padx=10, pady=5)

etiqueta_nombre_producto = ttk.Label(frame_entrada, text="Nombre del producto:")
etiqueta_nombre_producto.grid(row=1, column=0, padx=10, pady=5, sticky="e")

entrada_nombre_producto = ttk.Entry(frame_entrada, width=20)
entrada_nombre_producto.grid(row=1, column=1, padx=10, pady=5)

etiqueta_cantidad = ttk.Label(frame_entrada, text="Cantidad:")
etiqueta_cantidad.grid(row=2, column=0, padx=10, pady=5, sticky="e")

entrada_cantidad = ttk.Entry(frame_entrada, width=20)
entrada_cantidad.grid(row=2, column=1, padx=10, pady=5)

# Función para registrar la entrada de productos
def registrar_entrada():
    codigo_barras = entrada_codigo_barras.get()
    nombre = entrada_nombre_producto.get()
    cantidad = int(entrada_cantidad.get())

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM productos WHERE codigo_barras=%s", (codigo_barras,))
    producto = cursor.fetchone()

    if producto:
        nueva_cantidad = producto[2] + cantidad
        cursor.execute("UPDATE productos SET cantidad=%s WHERE codigo_barras=%s", (nueva_cantidad, codigo_barras))
    else:
        cursor.execute("INSERT INTO productos (codigo_barras, nombre, cantidad) VALUES (%s, %s, %s)", 
                       (codigo_barras, nombre, cantidad))

    conn.commit()
    cursor.close()
    conn.close()
    messagebox.showinfo("Éxito", "Producto registrado correctamente")
    limpiar_entradas()

# Función para registrar la salida de productos
def registrar_salida():
    codigo_barras = entrada_codigo_barras.get()
    cantidad = int(entrada_cantidad.get())

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM productos WHERE codigo_barras=%s", (codigo_barras,))
    producto = cursor.fetchone()

    if producto:
        nueva_cantidad = producto[2] - cantidad
        if nueva_cantidad >= 0:
            cursor.execute("UPDATE productos SET cantidad=%s WHERE codigo_barras=%s", (nueva_cantidad, codigo_barras))
            messagebox.showinfo("Éxito", "Producto retirado correctamente")
        else:
            messagebox.showerror("Error", "No hay suficiente stock")
    else:
        messagebox.showerror("Error", "Producto no encontrado")

    conn.commit()
    cursor.close()
    conn.close()
    limpiar_entradas()

# Limpiar los campos de entrada
def limpiar_entradas():
    entrada_codigo_barras.delete(0, tk.END)
    entrada_nombre_producto.delete(0, tk.END)
    entrada_cantidad.delete(0, tk.END)

# Función para buscar productos y mostrar los resultados en una nueva ventana
def buscar_producto():
    conn = conectar_db()
    cursor = conn.cursor()

    producto = entrada_nombre_producto.get()
    cursor.execute("SELECT * FROM productos WHERE nombre LIKE %s", ('%' + producto + '%',))
    resultado = cursor.fetchall()

    if resultado:
        # Crear una nueva ventana para mostrar los resultados
        ventana_resultados = tk.Toplevel(root)
        ventana_resultados.title("Resultados de búsqueda")
        ventana_resultados.geometry("400x300")
        
        # Crear un Treeview para mostrar los resultados
        tree = ttk.Treeview(ventana_resultados, columns=("Código de barras", "Nombre", "Cantidad"), show="headings")
        tree.heading("Código de barras", text="Código de barras")
        tree.heading("Nombre", text="Nombre")
        tree.heading("Cantidad", text="Cantidad")
        
        # Insertar los datos de los productos encontrados
        for producto in resultado:
            tree.insert("", tk.END, values=(producto[0], producto[1], producto[2]))

        tree.pack(fill=tk.BOTH, expand=True)
    else:
        messagebox.showerror("Error", "Producto no encontrado")

    conn.commit()
    cursor.close()
    conn.close()
    limpiar_entradas()

# Botones para registrar entradas y salidas
boton_entrada = ttk.Button(frame_botones, text="Registrar Entrada", command=registrar_entrada, width=20)
boton_entrada.grid(row=0, column=0, padx=10, pady=10)

boton_salida = ttk.Button(frame_botones, text="Registrar Salida", command=registrar_salida, width=20)
boton_salida.grid(row=0, column=1, padx=10, pady=10)

# Botón para buscar productos
boton_buscar = ttk.Button(frame_botones, text="Buscar Producto", command=buscar_producto, width=20)
boton_buscar.grid(row=1, column=0, padx=10, pady=10)

# Función para escanear el código de barras
def escanear_codigo_barras():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if ret:
            objetos_decodificados = decode(frame)
            for obj in objetos_decodificados:
                codigo_barras = obj.data.decode("utf-8")
                entrada_codigo_barras.delete(0, tk.END)
                entrada_codigo_barras.insert(0, codigo_barras)
                cap.release()
                return

root.mainloop()
