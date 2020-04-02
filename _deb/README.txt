mkdir simple-waf-builder
cd simple-waf-builder
git clone https://github.com/artempal/simple-django-waf.git
cd simple-django-waf
sudo apt-get install dpkg debconf debhelper lintian python3-venv md5deep
mv _deb/simple-waf ../
rm -rf _deb
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
cd ..
mkdir simple-waf/opt/simple-waf
mv simple-django-waf/* simple-waf/opt/simple-waf
chmod 755 simple-waf/DEBIAN/postinst
chmod 755 simple-waf/DEBIAN/prerm
chmod 755 simple-waf/DEBIAN/postrm
cd simple-waf
md5deep -l -o f -r opt -r lib -r etc > DEBIAN/md5sums
cd ..
chmod 755 simple-waf
chmod 755 simple-waf/*
deactivate
fakeroot dpkg-deb --build simple-waf
sudo dpkg -i simple-waf.deb
sudo apt-get install -f