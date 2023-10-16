from setuptools import setup,find_packages

 
setup(name='measurify',
    version='0.0.1',
    install_requires=["numpy","pandas","requests","urllib3"],
    packages=find_packages(),
    data_files=[('measurify/measurifyConfig.json')],
    py_modules=[]
)