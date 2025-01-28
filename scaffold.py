import os
from datetime import datetime
from colorama import Fore, Style
import inflect
import shutil

# Membuat objek engine inflect
p = inflect.engine()

def update_init_py(model_name):
    """Memperbarui __init__.py untuk menyertakan import model baru, menghindari duplikasi."""
    init_file = os.path.join("models", "__init__.py")
    
    # Menentukan import statement berdasarkan lokasi model
    if "/" in model_name:  # Jika model berada di subdirektori
        model_path = model_name.replace("/", ".")
        model_class = model_name.split("/")[-1].capitalize()
        import_statement = f"from .{model_path.lower()}_model import {model_class}"
    else:  # Jika model berada di direktori utama
        model_class = model_name.capitalize()
        import_statement = f"from .{model_name.lower()}_model import {model_class}"

    # Mendapatkan tanggal saat ini
    current_date = datetime.now().strftime("%Y-%m-%d")

    try:
        # Membaca file __init__.py
        with open(init_file, 'r') as f:
            lines = f.readlines()

        # Memeriksa apakah import_statement sudah ada dalam file
        if any(import_statement in line for line in lines):
            print(f"Model {model_name} sudah ada di {init_file}. Tidak ada perubahan.")
        else:
            # Menambahkan import statement jika belum ada
            with open(init_file, 'a') as f:
                f.write(f"\n# Ditambahkan pada {current_date} untuk model {model_name}\n")
                f.write(f"{import_statement}\n")
            print(f"Model {model_name} berhasil ditambahkan ke {init_file}.")
    
    except Exception as e:
        print(f"Error saat memperbarui {init_file}: {e}")

def create_file(file_path, content=""):
    """Membuat file dengan konten yang ditentukan."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"File {file_path} berhasil dibuat.")

def create_model(model_name, columns):
    """Fungsi untuk membuat model dan memperbarui __init__.py."""
    # Menentukan lokasi file model
    if "/" in model_name:
        model_path = os.path.join("models", model_name.lower().replace("/", "_"))
        os.makedirs(model_path, exist_ok=True)  # Membuat subdirektori jika belum ada
        model_file = os.path.join(model_path, f"{model_name.lower().split('/')[-1]}_model.py")
    else:
        model_file = os.path.join("models", f"{model_name.lower()}_model.py")

    # Menghasilkan konten untuk model
    model_content = generate_model_content(model_name, columns)
    
    # Membuat file model
    create_file(model_file, model_content)
    
    # Memperbarui __init__.py dengan import baru
    update_init_py(model_name)

def generate_model_content(model_name, columns):
    """Menghasilkan konten untuk file model SQLAlchemy."""

    # Mengumpulkan tipe data yang digunakan di kolom, termasuk tipe default
    types = {'Column', 'Integer', 'DateTime', 'ForeignKey'}

    # Menambahkan tipe data yang ada pada kolom
    for _, col_type in columns:
        # Ekstrak tipe data sebelum '(' jika ada
        base_type = col_type.split('(')[0]
        types.add(base_type)

    # Membuat statement import dinamis berdasarkan tipe data yang ditemukan
    base_import = (
        f"from sqlalchemy import {', '.join(sorted(types))}\n"
        "from sqlalchemy.sql import func\n"
        "from . import Base\n\n"
    )

    # Membentuk nama kelas dengan format PascalCase
    class_name = model_name.replace("_", " ").title().replace(" ", "")
    class_definition = f"class {class_name}(Base):\n    __tablename__ = '{model_name.lower()}s'\n\n"

    # Kolom default (id, created_by, updated_by, created_at, updated_at)
    id_column = "    id = Column(Integer, primary_key=True)\n"
    created_by_column = "    created_by = Column(Integer, ForeignKey('users.id'))\n"
    updated_by_column = "    updated_by = Column(Integer, ForeignKey('users.id'))\n"
    created_at_column = "    created_at = Column(DateTime, default=func.now())\n"
    updated_at_column = "    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())\n"

    # Definisi kolom tambahan berdasarkan parameter 'columns'
    columns_definition = "\n".join([f"    {name} = Column({col_type})" for name, col_type in columns])

    # Menggabungkan semua bagian menjadi satu string
    return (
        base_import
        + class_definition
        + id_column
        + columns_definition
        + "\n"
        + created_by_column
        + created_at_column
        + updated_by_column
        + updated_at_column
        + "\n"
    )

def prompt_columns():
    """Meminta input untuk mendefinisikan kolom model dengan validasi dan parameter default."""
    valid_types = {
        "Integer": None,
        "String": "255",  # Panjang default untuk String
        "Text": None,
        "Boolean": None,
        "Date": None,
        "DateTime": None,
        "Float": None,
        "Numeric": None,  # Bisa menggunakan presisi dan skala
        "BigInteger": None,
        "SmallInteger": None,
        "Binary": None,
        "Enum": None  # Enum memerlukan nilai eksplisit
    }
    columns = []
    
    print(Fore.CYAN + "Tentukan kolom untuk model Anda (misalnya, name:String(255), age:Integer). Ketik 'done' jika selesai." + Style.RESET_ALL)
    print(Fore.CYAN + "Tipe yang tersedia: " + ", ".join(valid_types.keys()) + Style.RESET_ALL)
    while True:
        column = input(Fore.CYAN + "Kolom (name:type): " + Style.RESET_ALL)
        if column.lower() == "done":
            break
        elif column.lower().startswith("id"):
            print(Fore.YELLOW + "Peringatan: Kolom 'id' sudah didefinisikan sebagai primary key." + Style.RESET_ALL)
            continue
        try:
            # Memisahkan input menjadi nama dan tipe kolom
            name, col_type = column.split(":")
            name, col_type = name.strip(), col_type.strip()

            # Menangani tipe kolom dengan parameter
            if "(" in col_type and ")" in col_type:
                base_type = col_type.split("(")[0].strip()
                if base_type not in valid_types:
                    print(Fore.RED + f"Error: '{base_type}' bukan tipe yang valid. Gunakan salah satu dari: {', '.join(valid_types.keys())}" + Style.RESET_ALL)
                    continue
            elif col_type in valid_types:
                # Menambahkan parameter default jika ada
                default_param = valid_types[col_type]
                if default_param:
                    col_type = f"{col_type}({default_param})"
            else:
                print(Fore.RED + f"Error: '{col_type}' bukan tipe yang valid. Gunakan salah satu dari: {', '.join(valid_types.keys())}" + Style.RESET_ALL)
                continue

            # Menambahkan kolom ke dalam list
            columns.append((name, col_type))
        except ValueError:
            print(Fore.RED + "Error: Format tidak valid. Gunakan nama:type (misalnya, name:String)." + Style.RESET_ALL)
    return columns


def create_blueprints(kind, app_name, columns):
    """Membuat file blueprint dan rutenya untuk aplikasi."""
    if kind == "forms.py":
        create_forms(app_name, columns)
    elif kind == "routes.py":
        create_routes(app_name, columns)
    else:
        print(f"Kind '{kind}' tidak dikenali. Gunakan 'forms.py' atau 'routes.py'.")

def create_forms(app_name, columns):
    print("columns: ", columns)
    """Membuat file forms.py untuk aplikasi dengan tipe kolom khusus."""
    forms_path = f"blueprints/{app_name.lower()}/forms.py"

    # Membuat konten untuk file forms.py
    form_fields = []

    for name, col_type in columns:
        if 'String' in col_type:
            length = int(col_type.split('(')[1].split(')')[0])  # Mengambil panjang String
            form_fields.append(f"    {name} = StringField('{name.capitalize()}', render_kw={{'maxlength': {length}}})")
        elif 'Enum' in col_type:
            # Ekstrak nilai enum dan buat tuple untuk choices
            enum_values = col_type.split('(')[1].split(')')[0].replace("'", "").split(',')
            choices = [(v, v) for v in enum_values]
            form_fields.append(f"    {name} = SelectField('{name.capitalize()}', choices={choices}, coerce=str)")
        elif 'Decimal' in col_type:
            form_fields.append(f"    {name} = DecimalField('{name.capitalize()}')")
        elif 'Integer' in col_type:
            form_fields.append(f"    {name} = IntegerField('{name.capitalize()}', validators=[NumberRange(min=0)])")
    
    columns_definition = "\n".join(form_fields)

    forms_content = f"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, SelectField
from wtforms.validators import DataRequired, NumberRange

class {app_name}Form(FlaskForm):
{columns_definition}

    def __init__(self, *args, **kwargs):
        super({app_name}Form, self).__init__(*args, **kwargs)
        # Tidak ada relasi atau data terkait untuk field ini
"""

    # Membuat file forms.py dan menulis kontennya
    create_file(forms_path, forms_content)
    print(f"File forms.py untuk {app_name} berhasil dibuat di {forms_path}.")

def create_routes(app_name, columns):
     # Membuat __init__.py untuk blueprint
    app_name_pluralize = p.plural(app_name.lower())
    app_name_singularize = app_name.lower()

    object_new_saved = "\n".join([f"            {column[0]} = form.{column[0]}.data," for column in columns])
    object_edit_saved = "\n".join([f"            {app_name_singularize}.{column[0]} = form.{column[0]}.data" for column in columns])

    init_blueprint_path = f"blueprints/{app_name_singularize}/__init__.py"
    init_blueprint_content = f"""from flask import Blueprint

{app_name_singularize}_bp = Blueprint('{app_name_singularize}', __name__, template_folder='templates')

from . import routes  # Memanggil routes.py untuk mendefinisikan rute
"""
    create_file(init_blueprint_path, init_blueprint_content)
    print(f"Blueprint __init__.py untuk {app_name} berhasil dibuat di {init_blueprint_path}.")

    """Membuat file routes.py untuk aplikasi."""
    routes_path = f"blueprints/{app_name_singularize}/routes.py"

    routes_content = f"""from flask import render_template, request, redirect, url_for, flash, session
from . import {app_name_singularize}_bp

from sqlalchemy.orm import joinedload
from models import get_session
from models.{app_name_singularize}_model import {app_name}
# Tambahkan model-model yang diperlukan

from .forms import {app_name}Form

@{app_name_singularize}_bp.route('/{app_name_pluralize}')
def lists():
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        {app_name_pluralize} = db_session.query({app_name}).options(
            # Tambahkan eager loading jika diperlukan
        ).all()

    finally:
        db_session.close()

    return render_template('{app_name_pluralize}/index.html', {app_name_pluralize}={app_name_pluralize})

@{app_name_singularize}_bp.route('/{app_name_singularize}/new', methods=['GET', 'POST'])
def new():
    form = {app_name}Form()
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # Ambil data tambahan jika diperlukan

    if form.validate_on_submit():
        # Menambahkan {app_name_singularize} baru
        {app_name_singularize} = {app_name}(
            # Ambil data dari form
{object_new_saved}
            created_by=session['user_id'],
            updated_by=None
        )
        db_session.add({app_name_singularize})
        db_session.commit()
        db_session.close()
        flash('{app_name} created successfully!', 'success')
        return redirect(url_for('{app_name_singularize}.lists'))
    db_session.close()
    return render_template('{app_name_pluralize}/new.html', form=form)

@{app_name_singularize}_bp.route('/{app_name_singularize}/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        {app_name_singularize} = db_session.query({app_name}).get(id)
        if not {app_name_singularize}:
            flash('{app_name} not found!', 'danger')
            return redirect(url_for('{app_name_singularize}.lists'))

        form = {app_name}Form(obj={app_name_singularize})

        if form.validate_on_submit():
            # Update data
{object_edit_saved}
            {app_name}.updated_by = session['user_id']

            db_session.commit()
            flash('{app_name} updated successfully!', 'success')
            return redirect(url_for('{app_name_singularize}.lists'))

        # Debug jika validasi form gagal
        if not form.validate_on_submit():
            flash(form.errors, 'danger')

        return render_template('{app_name_pluralize}/edit.html', form=form, {app_name_singularize}={app_name_singularize})

    except Exception as e:
        db_session.rollback()
        flash('An error occurred while editing {app_name}.', 'danger')
        print("Error:", e)
        return redirect(url_for('{app_name_singularize}.lists'))
    finally:
        db_session.close()

@{app_name_singularize}_bp.route('/{app_name_singularize}/<int:id>')
def show(id):
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    {app_name_singularize} = db_session.query({app_name}).get(id)

    db_session.close()
    if not {app_name_singularize}:
        flash('{app_name} not found!', 'danger')
        return redirect(url_for('{app_name_singularize}.lists'))
    return render_template('{app_name_pluralize}/show.html', {app_name_singularize}={app_name_singularize})
"""
    create_file(routes_path, routes_content)
    print(f"Routes untuk {app_name} berhasil dibuat di {routes_path}.")

def create_templates(app_name, columns):
    """Membuat file template HTML untuk aplikasi."""
    # Menggunakan inflect untuk membuat bentuk jamak dari nama aplikasi
    app_name_pluralize = p.plural(app_name.lower())

    templates_path = f"templates/{app_name_pluralize}/"
    os.makedirs(templates_path, exist_ok=True)

    # Path ke direktori scaffold_forms yang berisi template dasar
    scaffold_path = "scaffold_forms/"

    # Daftar file template yang akan disalin
    template_files = ["index.html", "new.html", "edit.html", "show.html", "form.html"]

    for template_name in template_files:
        # Menyalin template dari scaffold_forms ke templates/{app_name_pluralize}/
        template_file_path = os.path.join(scaffold_path, template_name)
        new_template_file_path = os.path.join(templates_path, template_name)
        shutil.copy(template_file_path, new_template_file_path)
        print(f"Template {template_name} untuk {app_name} berhasil dibuat di {templates_path}{template_name}.")

        # Membaca konten template yang baru disalin
        with open(new_template_file_path, 'r') as file:
            content = file.read()

        # Menggantikan placeholder {app_name} dan {app_name_pluralize} dengan nilai yang sesuai
        content = content.replace("{app_name}", app_name.capitalize())
        content = content.replace("{record}", app_name.lower())
        content = content.replace("{records}", app_name_pluralize)

        # Jika file adalah index.html, tambahkan logika dinamis untuk kolom
        if template_name == "index.html":
            # Membuat header <th> dengan indentasi
            th_columns = "\n".join([f"          <th>{col[0].capitalize()}</th>" for col in columns])            
            # Membuat data baris <td> dengan indentasi
            td_columns = "\n".join([f"          <td>{{{{ {app_name.lower()}.{col[0]} }}}}</td>" for col in columns])

            # Mengganti placeholder khusus dengan header dan data baris yang dibuat
            content = content.replace("{header_columns}", th_columns)
            content = content.replace("{data_columns}", td_columns)

        # Jika file adalah show.html, tambahkan logika dinamis untuk detail kolom
        if template_name == "show.html":
            # Membuat detail baris <div> dengan indentasi
            detail_columns = "\n".join(
                [f'      <div>{col[0].capitalize()}: {{{{ {app_name.lower()}.{col[0]} }}}}</div>' for col in columns]
            )

            # Mengganti placeholder khusus dengan detail baris yang dibuat
            content = content.replace("{detail_columns}", detail_columns)

        # Jika file adalah form.html, tambahkan logika dinamis untuk form input
        if template_name == "form.html":
            input_fields = ""
            for col in columns:
                field_name = col[0]
                field_type = col[1]

                if field_type.startswith("Enum"):
                    # Extracting enum values and creating a select field
                    enum_values = field_type[5:-1].split(",")  # Menghapus 'Enum(' dan ')'
                    enum_options = "\n".join([
                        f"""        <option value="{value.strip().strip("'").strip('"')}" {{% if {app_name.lower()} and {app_name.lower()}.{field_name} == '{value.strip().strip("'").strip('"')}' %}}selected{{% endif %}}>{value.strip().strip("'").strip('"')}</option>"""
                        for value in enum_values
                    ])
                    input_fields += f"""
                      <div class="row">
                        <div>
                          <label for="{field_name}">{field_name.capitalize()}</label>
                          <select id="{field_name}" name="{field_name}" class="form-control">
                    {enum_options}
                          </select>
                        </div>
                      </div>"""
                else:
                    # Default input type for other columns
                    input_fields += f"""
                      <div class="row">
                        <div>
                          <label for="{field_name}">{field_name.capitalize()}</label>
                          <input type="text" id="{field_name}" name="{field_name}" value="{{{{ {app_name.lower()}.{field_name} if {app_name.lower()} else '' }}}}" class="form-control">
                        </div>
                      </div>"""

            content = content.replace("{input_fields}", input_fields)
        
        # Menyimpan kembali konten yang telah diperbarui
        with open(new_template_file_path, 'w') as file:
            file.write(content)

def blueprints_register(app_name):
    """Menambahkan baris register blueprint pada app.py untuk aplikasi yang diberikan."""
    
    # Path untuk file app.py
    app_file_path = os.path.join(os.getcwd(), 'app.py')
    
    # Mencari semua subdirektori dalam folder blueprints, kecuali __pycache__
    blueprints_dir = os.path.join(os.getcwd(), 'blueprints')
    blueprint_names = [name for name in os.listdir(blueprints_dir) 
                       if os.path.isdir(os.path.join(blueprints_dir, name)) and name == app_name.lower()]
    
    # Mendapatkan tanggal saat ini
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Template import dan register blueprint
    import_statements = []
    register_statements = []
    
    for blueprint in blueprint_names:
        print(f"from blueprints.{blueprint}.routes import {blueprint}_bp")
        import_statements.append(f"from blueprints.{blueprint}.routes import {blueprint}_bp")
        register_statements.append(f"app.register_blueprint({blueprint}_bp)")
    
    # Membaca file app.py dan memastikan tidak ada duplikat
    try:
        with open(app_file_path, 'r') as f:
            content = f.read()
        
        # Memeriksa jika import dan register blueprint sudah ada
        if any(f"from blueprints.{blueprint}.routes import {blueprint}_bp" in content for blueprint in blueprint_names):
            print(f"from blueprints.{blueprint}.routes import {blueprint}_bp")
            print(f"Blueprints sudah terdaftar di {app_file_path}.")
            return
        
        # Menambahkan import statement pada bagian atas file
        import_block = "\n".join(import_statements)
        register_block = "\n".join(register_statements)
        
        # Menambahkan import dan register blueprint sebelum kode aplikasi utama
        content = content.replace(
            "# Register blueprints by scaffold",
            f"# Register blueprints by scaffold\n{import_block}\n\n{register_block}\n"
        )

        print("import_block: ", import_block)
        print("register_block: ", register_block)
        
        # Menulis ulang file app.py dengan perubahan
        with open(app_file_path, 'w') as f:
            f.write(content)
        
        print(f"Blueprints berhasil didaftarkan di {app_file_path} pada {current_date}.")
    
    except Exception as e:
        print(f"Terjadi kesalahan saat memperbarui {app_file_path}: {e}")


def scaffold(app_name):
    """Fungsi utama untuk melakukan scaffolding aplikasi."""
    # Prompt untuk kolom
    columns = prompt_columns()

    # Membuat Model
    create_model(app_name, columns)

    # Membuat Blueprints
    create_blueprints('forms.py', app_name, columns)
    create_blueprints('routes.py', app_name, columns)

    # Membuat Templates
    create_templates(app_name, columns)

    # register app.py
    blueprints_register(app_name)

    print(f"Scaffold untuk {app_name} berhasil dibuat!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Penggunaan: python scaffold.py <AppName>")
    else:
        app_name = sys.argv[1]
        scaffold(app_name)
