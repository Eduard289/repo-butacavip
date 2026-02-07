import os
import hashlib
import zipfile
import re
import shutil

class Generator:
    def __init__(self):
        # Directorio actual donde esta el script
        self.source_path = os.getcwd()
        # Archivos maestros del repositorio
        self.addons_xml = os.path.join(self.source_path, "addons.xml")
        self.addons_xml_md5 = os.path.join(self.source_path, "addons.xml.md5")
        
        # LISTA NEGRA: Archivos y carpetas que NO queremos en el ZIP
        self.ignore_extensions = ['.pyc', '.pyo', '.git', '.DS_Store', '.zip']
        self.ignore_folders = ['__pycache__', '.git', '.idea', '.vscode', 'repository.butacavip'] 
        self.ignore_files = ['generator.py', 'inspector.py', 'analizar_interno.py', 'analisis.py', 'REPORTE_ELEMENTUM.txt']

    def run(self):
        print(f"🚀 Iniciando generador de repositorio en: {self.source_path}")
        self._generate_addons_file()
        self._generate_md5_file()
        print("\n✅ ¡Proceso finalizado! Repositorio listo para subir.")

    def _should_ignore(self, file_name):
        # Filtra archivos basura y herramientas
        if file_name in self.ignore_files: return True
        if any(file_name.endswith(ext) for ext in self.ignore_extensions): return True
        return False

    def _get_version(self, addon_xml_path):
        # Abre el addon.xml y busca texto tipo: version="0.0.1"
        try:
            with open(addon_xml_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Regex que busca el atributo version="..."
                match = re.search(r'version="([^"]+)"', content)
                if match:
                    return match.group(1)
        except Exception as e:
            print(f"⚠️ Error leyendo versión: {e}")
        return "0.0.0"

    def _generate_addons_file(self):
        xml_content = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<addons>\n"
        found_addons = False
        
        # Recorre todas las carpetas del directorio
        for folder in os.listdir(self.source_path):
            folder_path = os.path.join(self.source_path, folder)
            xml_file = os.path.join(folder_path, "addon.xml")

            # Solo procesamos carpetas que sean addons (tienen addon.xml)
            if os.path.isdir(folder_path) and os.path.isfile(xml_file):
                if folder.startswith(".") or folder in self.ignore_folders: 
                    continue
                
                found_addons = True
                try:
                    # 1. Detectar versión real del XML
                    version = self._get_version(xml_file)
                    print(f"\n📦 Procesando Addon: {folder}")
                    print(f"   └── Versión detectada: {version}")
                    
                    # 2. Generar el ZIP con el nombre CORRECTO
                    self._create_zip_clean(folder, version)

                    # 3. Añadir info al XML maestro (addons.xml)
                    with open(xml_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        for line in lines:
                            # Copiamos todo menos la primera línea (<?xml...)
                            if line.find("<?xml") == -1:
                                xml_content += line.rstrip() + "\n"
                    xml_content += "\n"

                except Exception as e:
                    print(f"❌ Error procesando {folder}: {e}")

        xml_content += "</addons>\n"
        
        if found_addons:
            with open(self.addons_xml, "w", encoding="utf-8") as f:
                f.write(xml_content)
            print(f"\n📄 Archivo índice 'addons.xml' generado correctamente.")
        else:
            print("⚠️ No se encontraron addons en esta carpeta.")

    def _create_zip_clean(self, folder_name, version):
        # Nombre exacto: plugin.video.butacavip-0.0.1.zip
        zip_name = f"{folder_name}-{version}.zip"
        folder_path = os.path.join(self.source_path, folder_name)
        zip_path = os.path.join(folder_path, zip_name)

        # Borrar zip anterior si existe para evitar duplicados o errores
        if os.path.exists(zip_path):
            os.remove(zip_path)
            print(f"   🗑️  Borrado ZIP antiguo: {zip_name}")

        # Crear nuevo ZIP
        print(f"   🔨 Comprimiendo: {zip_name} ...")
        zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
        
        for root, dirs, files in os.walk(folder_path):
            # Filtrar carpetas ignoradas in-situ
            dirs[:] = [d for d in dirs if d not in self.ignore_folders]
            
            for file in files:
                if not self._should_ignore(file):
                    file_path = os.path.join(root, file)
                    # La ruta dentro del zip debe mantener la estructura folder_name/archivo
                    archive_name = os.path.join(folder_name, os.path.relpath(file_path, folder_path))
                    zipf.write(file_path, archive_name)
        
        zipf.close()
        print(f"   ✅ ZIP Creado: {zip_name}")

    def _generate_md5_file(self):
        try:
            with open(self.addons_xml, "rb") as f:
                md5_hash = hashlib.md5(f.read()).hexdigest()
            with open(self.addons_xml_md5, "w", encoding="utf-8") as f:
                f.write(md5_hash)
            print("🔐 Archivo de verificación 'addons.xml.md5' generado.")
        except Exception as e:
            print(f"❌ Error MD5: {e}")

if __name__ == "__main__":
    Generator().run()