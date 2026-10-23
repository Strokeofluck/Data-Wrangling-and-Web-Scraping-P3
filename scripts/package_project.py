"""Create a credential-free ZIP of the complete project for download/Colab."""
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def package(destination=None):
    destination=Path(destination) if destination else ROOT.parent/'P3-project.zip'
    omitted={'.git','__pycache__','.venv','.ipynb_checkpoints'}
    with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for path in sorted(ROOT.rglob('*')):
            relative=path.relative_to(ROOT)
            if any(part in omitted for part in relative.parts):continue
            if relative.parts[:2]==('data','work'):continue
            if path.is_file():archive.write(path,Path('P3')/relative)
    print(f'Packaged {destination.name}: {destination.stat().st_size/1e6:.1f} MB')
    return destination

if __name__=='__main__':package()
