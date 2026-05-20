# B2B Custom CRM Intelligence

## Project Overview
Este proyecto simula el desarrollo de la infraestructura de datos y el panel analítico de un CRM personalizado (Custom CRM) para un entorno de ventas B2B. A diferencia de un análisis exploratorio tradicional basado en archivos estáticos, este repositorio implementa una **arquitectura relacional completa**, un **motor de procesamiento de reglas de negocio** y una **capa de visualización interactiva**. Está diseñado para transformar datos crudos en un sistema integral de toma de decisiones y gestión de clientes.

## Business Problem
Una empresa tecnológica B2B de tamaño mediano se enfrenta a problemas de fragmentación de datos. Su información comercial está dividida en múltiples archivos estáticos y desordenados: por un lado, métricas generales de las cuentas corporativas (empresas) y por otro, una lista masiva de los contactos individuales dentro de esas cuentas (empleados). 

Esta desconexión genera problemas críticos para el negocio:
1. **Falta de visibilidad:** Los líderes de ventas no pueden cruzar fácilmente el desempeño de las campañas de marketing corporativas con la tasa de respuesta individual de los tomadores de decisiones.
2. **Oportunidades perdidas:** Los representantes de ventas carecen de un sistema automatizado que priorice a qué clientes contactar basándose en su nivel de influencia (*Contact Scoring*) o cuentas que corren riesgo de abandonar el servicio (*Churn Risk*).
3. **Ineficiencia operativa:** Los analistas de datos pierden horas valiosas cada semana limpiando datos ruidosos y cruzando tablas manualmente en Excel para armar reportes estáticos.

**La solución:** Migrar esta información fragmentada a una base de datos relacional centralizada mediante un pipeline automatizado (ETL). Sobre esta estructura sólida, construir un motor de reglas de negocio que alimente un Dashboard interactivo, dotando al equipo de ventas de inteligencia accionable en tiempo real.

## Objectives
*   **Arquitectura de Datos (Data Engineering):** Migrar datos planos (CSV) hacia una base de datos relacional (SQLite) garantizando la integridad referencial entre empresas (Companies), contactos (Employees) y representantes de ventas (Sales Reps).
*   **Lógica de Negocio (Backend):** Desarrollar scripts modulares en Python que automaticen la limpieza de datos y ejecuten reglas de negocio (ej. cálculo de Engagement Score, detección de contratos expirados).
*   **Visualización Interactiva (BI):** Construir un dashboard analítico que consulte directamente la base de datos para monitorear el pipeline, la respuesta a campañas y el rendimiento del equipo.
*   **Automatización:** Establecer un pipeline base que permita el mantenimiento fluido y la escalabilidad de la estructura del CRM.

## Tech Stack
*   **Lenguaje:** Python 3.x
*   **Base de Datos:** SQLite (Motor relacional)
*   **Procesamiento y ORM:** Pandas, SQLAlchemy
*   **Visualización:** Streamlit, Plotly
*   **Entorno de Desarrollo:** Antigravity (Google Agentic Editor)

## Project Structure
```text
├── data/               # Datasets originales B2B (empresas y empleados)
├── database/           # Archivo .db generado y scripts de migración
├── src/                # Código fuente modular
│   ├── models.py       # Definición de clases y esquema SQL (Companies, Employees, SalesReps)
│   ├── processor.py    # Lógica de limpieza, formateo y carga inicial (ETL)
│   └── business.py     # Lógica de negocio (Cálculo de KPIs y Scoring)
├── app/                # Frontend (Dashboard interactivo en Streamlit)
├── notebooks/          # Exploración inicial de datos y pruebas (EDA)
├── README.md           # Documentación principal del proyecto
└── requirements.txt    # Dependencias de Python