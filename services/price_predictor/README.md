# Data Validation
for checking data quality:
- great-expectations
- Evidently
- Deep checks

Генерируем отчёт о качестве данных внутри training pipeline. Отсылаем отчёт в трекер CometML


# Santiment
 alpaca.markets - API websocket с новостями - можно использовать для определения сантимента.



# Установка TA-Lib
> wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install


> sudo ldconfig


> poetry add TA-Lib



# Работа с кубернетес
https://paulabartabajo.substack.com/p/lets-deploy-our-rest-api-to-production


low cost dedicated servers from Hetzner, OVH