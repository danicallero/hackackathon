# Hackackathon

Un proyecto hecho con Django para la gestión de hackackatones.

## Instrucciones para desarrollo

Después de clonar el repositorio, sigue estos pasos para iniciar el desarrollo:

1. Definir variables de entorno.\
   Renombra `plantilla.env` a `.env` y fija los valores de las variables.
2. Crear el entorno virtual de Python e instalar las dependencias (`requirements.txt`).
3. Crear la base de datos con las migraciones existentes:\
   `python manage.py migrate`
4. Cargar la tabla de restricciones alimentarias:\
   `python manage.py loadddata restriccion_alimentaria`
5. Crea un superusuario: \
   `python manage.py createsuperuser` (puedes dejar el correo en blanco)
6. (Opcional) Generar Participantes de ejemplo:\
   `python manage.py fakeuserdata <cantidad>`

## Diagrama Entidad-Relación de los modelos

```mermaid
erDiagram

    PERSONAABSTRACTA {
        string correo PK
        string nombre
        text notas
        string acreditacion
    }

    PATROCINADOR {
        string correo PK, FK
        string empresa
    }

    PERSONA {
        string correo PK, FK
        string dni
        string genero
        string talla_camiseta
        file cv
        bool compartir_cv
        datetime fecha_registro
        datetime fecha_verificacion_correo
        datetime fecha_aceptacion
        datetime fecha_confirmacion_plaza
    }

    MENTOR {
        string correo PK, FK
    }

    PARTICIPANTE {
        string correo PK, FK
        string telefono
        int ano_nacimiento
        string nivel_estudio
        string nombre_estudio
        string centro_estudio
        string curso
        string ciudad
        bool quiere_creditos
        text motivacion
    }

    RESTRICCIONALIMENTARIA {
        int id_restriccion PK
        string nombre
    }

    PRESENCIA {
        int id_presencia PK
        datetime entrada
        datetime salida
        string persona_id FK
    }

    TIPOPASE {
        int id_tipo_pase PK
        string nombre
        datetime inicio_validez
    }

    PASE {
        int id_pase PK
        string persona_id FK
        int tipo_pase_id FK
        datetime fecha
    }

    TOKEN {
        uuid token PK
        string tipo
        string persona_id FK
        datetime fecha_creacion
        datetime fecha_expiracion
        datetime fecha_uso
    }

    %% Relaciones
    PERSONAABSTRACTA ||--o{ RESTRICCIONALIMENTARIA : "restricciones_alimentarias"
    PERSONA ||--o{ PRESENCIA : "tiempo_acceso"
    PERSONA ||--o{ PASE : "pases"
    PERSONA ||--o{ TOKEN : "tokens"

    TIPOPASE ||--o{ PASE : "pases"

    %% Herencia
    PERSONAABSTRACTA ||--|{ PERSONA : ""
    PERSONAABSTRACTA ||--|{ PATROCINADOR : ""
    PERSONA ||--|{ MENTOR : ""
    PERSONA ||--|{ PARTICIPANTE : ""
```

## Licencia

El proyecto está bajo la licencia AGPLv3, para más info ver [la licencia](LICENSE).
