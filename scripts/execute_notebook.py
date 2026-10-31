"""Execute the submitted notebook in a fresh kernel using this Python environment."""
from pathlib import Path
import sys,json,os,tempfile
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager
from nbconvert import HTMLExporter

ROOT=Path(__file__).resolve().parents[1]

def execute():
    keys=['IPYTHONDIR','JUPYTER_RUNTIME_DIR']
    previous={key:os.environ.get(key) for key in keys}
    try:
        with tempfile.TemporaryDirectory(prefix='p3-notebook-') as folder:
            temporary=Path(folder)
            os.environ['IPYTHONDIR']=str(temporary/'ipython')
            os.environ['JUPYTER_RUNTIME_DIR']=str(temporary/'runtime')
            kernel=temporary/'kernels/p3';kernel.mkdir(parents=True)
            (kernel/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'P3 fresh kernel','language':'python'}))
            manager=KernelManager(kernel_name='p3',kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernel.parent)]))
            path=ROOT/'notebooks/DSA405_002_FA26_P3_sryan3.ipynb'
            notebook=nbformat.read(path,as_version=4)
            client=NotebookClient(notebook,km=manager,timeout=180,resources={'metadata':{'path':str(ROOT)}})
            try:
                client.execute()
            finally:
                # nbclient does not own a supplied manager. Stop it explicitly
                # before Windows attempts to remove the temporary SQLite files.
                if manager.has_kernel:manager.shutdown_kernel(now=True)
            nbformat.validate(notebook)
            nbformat.write(notebook,path)
            html,_=HTMLExporter(template_name='lab').from_notebook_node(notebook)
            html='\n'.join(line.rstrip() for line in html.splitlines())+'\n'
            (ROOT/'docs/P3-notebook.html').write_text(html,encoding='utf-8',newline='\n')
            print('Executed',sum(c.cell_type=='code' for c in notebook.cells),'code cells successfully. Exported docs/P3-notebook.html.')
    finally:
        for key,value in previous.items():
            if value is None:os.environ.pop(key,None)
            else:os.environ[key]=value

if __name__=='__main__':execute()
