# Processo Seletivo: Iniciação Científica em IA multimodal na triagem de Raios-X

O arquivo `script.py` contém a função que envia arquivos DICOM para o servidor local. `python script.py` envia os arquivos em `data/` para o servidor.

O arquivo `classify.py` computa os resultados de classificação utilizando o modelo pré-treinado. `python classify.py` faz a classificação e salva os resultados no arquivo `results.json`. Para facilitar a criação do DICOM SR, o formato escolhido para salvar os resultados é `caminho: resultado`.

O arquivo `send_results.py` cria um DICOM SR para cada resultado obtido e envia para o servidor local. O SR é salvo no formato `.dcm` na pasta `dicom_results/`.

## Comentários

- Minha maior fonte de dificuldades durante o projeto foi o Docker. Eu não tinha experiência prévia com ele, e achei difícil configurar e rodar o servidor. 
- A coisa que aprendi e achei mais interessante foi a "filosofia" geral na área médica. Me parece que a ideia é buscar robustez. Por exemplo, imagens geralmente são comprimidas de maneira lossless [1]; algumas tags DICOM tem identificadores únicos _globais_ [1]; os modelos precisam ser bem calibrados; etc.

## Referências

- [1] https://orthanc.uclouvain.be/book/dicom-guide.html