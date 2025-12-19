# 💰 Finance App - Gestión Financiera & Educación con IA

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-lightgrey?style=for-the-badge&logo=flask&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-Design-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-Database-orange?style=for-the-badge&logo=firebase&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-Machine%20Learning-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)

**Finance App** es una plataforma web integral diseñada para democratizar el conocimiento financiero. No solo permite a los usuarios gestionar sus finanzas personales, sino que integra un **Módulo Educativo Inteligente** impulsado por Machine Learning y simulaciones de mercado basadas en datos históricos.

---

## 🚀 Características Principales

### 📊 Gestión Financiera Personal
* **Control de Gastos e Ingresos:** Registro detallado de transacciones.
* **Planificador de Presupuestos:** Herramienta interactiva para establecer límites de gasto por categoría.
* **Dashboard en Tiempo Real:** Visualización de métricas clave de salud financiera.

### 🧠 Centro de Inteligencia Artificial (AI Hub)
* **Analista de Perfil con IA:** Un modelo de Machine Learning (**Random Forest**) que analiza datos demográficos y financieros del usuario para predecir su Perfil de Inversionista (*Conservador, Moderado, Agresivo*).
* **Simulador de Mercado (Gamification):** Un juego interactivo donde los usuarios toman decisiones de compra/venta basadas en noticias históricas reales y análisis de sentimiento de mercado.
* **Escuela de Inversiones:** Biblioteca de conceptos financieros fundamentales.

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Descripción |
| :--- | :--- | :--- |
| **Backend** | Python 3.12, Flask | Uso de *Blueprints* para arquitectura modular. |
| **Frontend** | HTML5, Jinja2, Tailwind CSS | Diseño responsivo y moderno. |
| **Base de Datos** | Google Firebase | Firestore NoSQL. |
| **Data Science** | Pandas, Scikit-Learn, Joblib | Procesamiento de datos y modelos predictivos. |
| **Control de Versiones** | Git & GitHub | Flujo Feature -> QA -> Main. |

---


## 📂 Arquitectura del Proyecto

El proyecto sigue una estructura modular **MVC (Modelo-Vista-Controlador)** adaptada a Flask:

```text
Finance/
│
├── app.py                 # Punto de entrada de la aplicación
├── requirements.txt       # Dependencias del proyecto
├── .env                   # Variables de entorno (Credenciales)
│
├── blueprints/            # Controladores (Rutas)
│   ├── auth.py            # Autenticación de usuarios
│   ├── main.py            # Lógica principal del Dashboard
│   ├── budget.py          # Lógica de presupuestos
│   └── learning.py        # Controlador de la Escuela y la IA
│
├── modelos/               # 🧠 MÓDULO DE MACHINE LEARNING
│   ├── data/              # Datos crudos para entrenamiento (CSV)
│   ├── binarios/          # Modelos entrenados (.pkl) y Encoders
│   ├── entrenar.py        # Script de entrenamiento (Generador de cerebro)
│   └── predecir.py        # Motor de inferencia para la App Web
│
├── templates/             # Vistas (HTML)
│   ├── layout.html        # Plantilla base
│   └── learning/          # Vistas del módulo educativo
│       ├── index.html     # Menú principal de la escuela
│       ├── test_ia.html   # Formulario para el análisis de perfil
│       └── game.html      # Interfaz del simulador de mercado
│
└── static/                # Archivos estáticos (CSS, JS, Imágenes)


