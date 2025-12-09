# Hackackathon

Un proyecto hecho con Django para la gestión de hackackatones.

## Instrucciones para desarrollo

Después de clonar el repositorio, sigue estos pasos para iniciar el desarrollo:

1. Definir variables de entorno.\
   Renombra `plantilla.env` a `.env` y fija los valores de las variables.
1. Crear el entorno virtual de Python e instalar las dependencias (`requirements.txt`).
1. Crear la base de datos con las migraciones existentes:\
   `python manage.py migrate`
1. Cargar la tabla de restricciones alimentarias:\
   `python manage.py loadddata restriccion_alimentaria`
1. Crea un superusuario:\
   `python manage.py createsuperuser` (puedes dejar el correo en blanco)
1. Crea los grupos base y asigna los permisos:\
   `python manage.py crear_permisos_grupos`
1. (Opcional) Generar Participantes de ejemplo:\
   `python manage.py fakeuserdata <cantidad>`

## Diagrama Entidad-Relación de los modelos

```mermaid
erDiagram

    %% No almacenado en BD.
    PERSONAABSTRACTA {
        string correo PK
        string nombre
        text notas
        string acreditacion
        text detalle_restricciones_alimentarias
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
        datetime fecha_rechazo_plaza
        text motivo_error_correo_verificacion
    }

    MENTOR {
        string correo PK, FK
        string telefono
        date fecha_nacimiento
        string ciudad
        bool quiere_creditos
        text motivacion
    }

    PARTICIPANTE {
        string correo PK, FK
        string telefono
        date fecha_nacimiento
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
        string persona_id FK
        datetime entrada
        datetime salida
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
    PERSONAABSTRACTA ||--o{ RESTRICCIONALIMENTARIA : ""
    PERSONA ||--o{ PRESENCIA : ""
    PERSONA ||--o{ PASE : ""
    PERSONA ||--o{ TOKEN : ""

    TIPOPASE ||--o{ PASE : ""

    %% Herencia
    PERSONAABSTRACTA ||--|{ PATROCINADOR : ""
    PERSONAABSTRACTA ||--|{ PERSONA : ""
    PERSONA ||--|{ PARTICIPANTE : ""
    PERSONA ||--|{ MENTOR : ""
```

## Licencia

El proyecto está bajo la licencia AGPLv3, para más info ver [la licencia](LICENSE).
