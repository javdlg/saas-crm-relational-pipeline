# B2B Custom CRM Intelligence

## Project Overview
Este proyecto simula el desarrollo de la infraestructura de datos y el panel analítico de un CRM personalizado (Custom CRM) para un entorno de ventas B2B. A diferencia de un análisis exploratorio tradicional basado en archivos estáticos, este repositorio implementa una **arquitectura relacional completa**, un **motor de procesamiento de reglas de negocio** y una **capa de visualización interactiva**. Está diseñado para transformar datos crudos en un sistema integral de toma de decisiones y gestión de clientes.

## Objectives
*   **Arquitectura de Datos (Data Engineering):** Migrar datos planos (CSV) hacia una base de datos relacional (SQLite) garantizando la integridad referencial entre clientes, equipos de ventas y oportunidades.
*   **Lógica de Negocio (Backend):** Desarrollar scripts modulares en Python que automaticen la limpieza de datos y ejecuten reglas de negocio (ej. cálculo de Lead Scoring, detección de oportunidades estancadas).
*   **Visualización Interactiva (BI):** Construir un dashboard analítico que consulte directamente la base de datos para monitorear el embudo de ventas (Sales Funnel), la velocidad del pipeline y el rendimiento (Win Rate) del equipo.
*   **Automatización:** Establecer un pipeline base que permita el mantenimiento fluido y la escalabilidad de la estructura del CRM.

## Tech Stack
*   **Lenguaje:** Python 3.x
*   **Base de Datos:** SQLite (Motor relacional)
*   **Procesamiento y ORM:** Pandas, SQLAlchemy
*   **Visualización:** Streamlit, Plotly
*   **Entorno de Desarrollo:** Antigravity (Google Agentic Editor)

## Project Structure
```text
├── data/               # Datasets originales B2B (CSV)
├── database/           # Archivo .db generado y scripts de migración
├── src/                # Código fuente modular
│   ├── models.py       # Definición de clases y esquema SQL (SQLAlchemy)
│   ├── processor.py    # Lógica de limpieza, formateo y carga inicial (ETL)
│   └── business.py     # Lógica de negocio (Lead Scoring, cálculo de KPIs)
├── app/                # Frontend (Dashboard interactivo en Streamlit)
├── notebooks/          # Exploración inicial de datos y pruebas (EDA)
├── README.md           # Documentación principal del proyecto
└── requirements.txt    # Dependencias de Python