import os
import sys
from fabric.api import env, run, cd,  sudo, task, parallel, put, get, lcd
from fabric.contrib.files import exists

# REGION       = os.environ.get("AWS_EC2_REGION")
# WEB_ROOT = "/var/www"

#execfile("stage.env")
execfile("prod.env")
#execfile("prod.old.env")


# Setup System and the OS Packages
@task
@parallel
def configApache():
    with cd('/tmp'):
        put('./config/apache/' + env.setup + '/000-default.conf', '000-default.conf')
        sudo('cat 000-default.conf > /etc/apache2/sites-enabled/000-default.conf')
        put('./config/apache/' + env.setup + '/ssl/modmed.com.ca', 'modmed.com.ca')
        put('./config/apache/' + env.setup + '/ssl/modmed.com.crt', 'modmed.com.crt')
        put('./config/apache/' + env.setup + '/ssl/modmed.com.key', 'modmed.com.key')
        if not exists('/etc/apache2/ssl'):
            sudo ('mkdir /etc/apache2/ssl')

        sudo ('cp modmed.com.ca /etc/apache2/ssl/')
        sudo ('cp modmed.com.crt /etc/apache2/ssl')
        sudo ('cp modmed.com.key /etc/apache2/ssl/')
        sudo ('chown -R root:root /etc/apache2/ssl/')
        sudo ('chmod -R 600 /etc/apache2/ssl/')

        sudo ('rm -rf modme.com.*')
        sudo ('rm -rf 000-default.conf')
        
        sudo ('a2enmod rewrite')
        sudo ('a2enmod ssl')
        sudo ('a2enmod headers')
        sudo ('a2enmod mpm_prefork')
        sudo ('a2ensite 000-default')
        sudo('service apache2 restart')

        sudo('mkdir -p /srv/www/default')
        sudo('rm -rf /srv/www/current')
        sudo('touch /srv/www/default/index.html')
        sudo('echo "Hello world." > /srv/www/default/index.html')
        sudo('ln -s  /srv/www/default/ /srv/www/current')


# Add the rest of the apache cong


# Setup System and the OS Packages
@task
@parallel
def setupSoftware():
    sudo('apt-get -y upgrade')
    sudo('apt-get update -y')
    sudo(
        'apt-get install -y libicu-dev wget libxml2-dev libzip-dev unzip libsqlite3-dev libbz2-dev zlib1g-dev libjpeg-dev libpng-dev libfreetype6-dev libmcrypt-dev php-dev')
    sudo('apt-get install -y apache2')
    sudo('apt-get install -y mysql-client')
    sudo('apt-get install -y software-properties-common')
    sudo('add-apt-repository -y universe')
    sudo('add-apt-repository -y ppa:certbot/certbot')
    sudo('add-apt-repository -y ppa:ondrej/php')
    sudo('apt-get update -y')
    # sudo('apt-get install -y certbot python-certbot-apache')
    sudo('apt-get install -y git openssh-client')
    sudo(
        'apt-get install -y php7.3-curl php7.3-cli php7.3 php7.3-cli php7.3-common php7.3-mbstring php7.3-gd php7.3-intl php7.3-xml php7.3-mysql php7.3-zip php7.3-bcmath php7.3-bz2')
    sudo('apt-get install -y php-pear')
    run('echo "yes\n"| sudo pecl install -f mcrypt-1.0.2')
    sudo('touch /etc/php/7.3/mods-available/mcrypt.ini')
    sudo('echo "extension=mcrypt.so" > /etc/php/7.3/mods-available/mcrypt.ini')
    sudo('ln -snf /etc/php/7.3/mods-available/mcrypt.ini /etc/php/7.3/apache2/conf.d/mcrypt.ini')
    sudo('ln -snf /etc/php/7.3/mods-available/mcrypt.ini /etc/php/7.3/cli/conf.d/mcrypt.ini')
    sudo('apt -y autoremove')


# sudo ('echo "yes\n"| pecl install pcntl')
# sudo ('echo "yes\n"| pecl install memcache')


# Create account for deployment. The user will not be able to loggedin.
# --system will not allow to loggedin.
@task
@parallel
def setupDeployAccount():
    # sudo ('groupdel deploy')
    sudo('userdel deploy')
    sudo('rm -rf /home/deploy')
    if not exists("/home/deploy"):
        sudo('adduser --home /home/deploy --disabled-password --gecos "" deploy')
        sudo("usermod -a -G admin deploy")
        sudo("mkdir /home/deploy/.ssh")
        sudo('ssh-keygen -f /home/deploy/.ssh/id_rsa -P "randomScript"')
        sudo("chmod -R 600 /home/deploy/.ssh")
        sudo("chown -R deploy:deploy /home/deploy/.ssh")


@task
@parallel
def setupUserSshIdRsaAccount():
    if not exists('/home/ubuntu/.ssh/id_rsa'):
        run('ssh-keygen -f /home/ubuntu/.ssh/id_rsa -P ""')
    run('cat /home/ubuntu/.ssh/id_rsa.pub')


@task
@parallel
def setupSshGitIp():
    sudo('chown ubuntu:ubuntu /home/ubuntu/.ssh/known_hosts')
    run('ssh-keygen -R management.ascendro.de')


@task
@parallel
def whoami():
    run('whoami')
    

@task
@parallel
def setupApachePrefork():
 with cd('/tmp'):
        put('./config/apache/' + env.setup + '/prefork/mpm_prefork.conf', 'mpm_prefork.conf')
        sudo('cat mpm_prefork.conf > /etc/apache2/sites-enabled/mpm_prefork.conf')
        sudo('cat /etc/apache2/sites-enabled/mpm_prefork.conf')
        sudo('rm -rf mpm_prefork.conf')
        sudo('service apache2 restart')
    


# Normlize the local server
@task
@parallel
def normalizeTheServer():
    # setupSoftware()
    configSoftware()

# Normlize the local server
@task
@parallel
def setupNewRelic():
    sudo('echo \'deb http://apt.newrelic.com/debian/ newrelic non-free\' | sudo tee /etc/apt/sources.list.d/newrelic.list')
    sudo('wget -O- https://download.newrelic.com/548C16BF.gpg | sudo apt-key add -')
    sudo('apt-get update -y')
    sudo('apt-get install -y newrelic-php5')
    sudo('newrelic-install install')


@task
@parallel
def installConfig():
    with cd('/srv/share/mmim/etc/config/'):
         #sudo('rm -rf main.php')
         put('./config/mmim/' + env.setup + '/main.php', 'main.php')
         #sudo('rm -rf aws-config.php')
         #put('./config/mmim/' + env.setup + '/aws-config.php', 'aws-config.php')
         #run('ln -snf /srv/share/mmim/etc/aws-config.php aws-config.php')
    #with cd('/srv/share/mmim/code/src/protected/config'):
    #     run('ln -snf /srv/share/mmim/etc/config/aws-config.php aws-config.php')
    #     run('ln -snf /srv/share/mmim/etc/config/cron.php cron.php')
    #     run('ln -snf /srv/share/mmim/etc/config/console.php console.php')



@task
@parallel
def copyAppMmimUploadsToLocal():
    sudo('chown -R ubuntu /srv/www/aesyntix/shared/uploads/')
    if not exists('/tmp/uploads.zip'):
        with cd('/srv/www/aesyntix/shared/uploads/'):
            sudo('zip -r /tmp/uploads.zip ./')
    sudo('chown ubuntu /tmp/uploads.zip')
    get('/tmp/uploads.zip', './tmp/uploads/uploads.zip')
    sudo ('rm -rf /tmp/uploads.zip', '.')
    sudo('chown -R deploy /srv/www/aesyntix/shared/uploads/')


@task
@parallel
def copyAppMmimImgCacheToLocal():
    sudo('chown -R ubuntu /srv/www/aesyntix/current/src/imgcache')
    if not exists('/tmp/imgcache.zip'):
        with cd('/srv/www/aesyntix/current/src/imgcache/'):
            sudo('zip -r /tmp/imgcache.zip ./')
    sudo('chown ubuntu /tmp/imgcache.zip')
    get('/tmp/imgcache.zip', './tmp/imgcache/imgcache.zip')
    sudo ('rm -rf /tmp/imgcache.zip', '.')
    sudo('chown -R deploy /srv/www/aesyntix/current/src/imgcache/')

@task
@parallel
def copyAppMmimExportsToLocal():
    sudo('chown -R ubuntu /srv/www/aesyntix/current/src/exports')
    if not exists('/tmp/exports.zip'):
        with cd('/srv/www/aesyntix/current/src/exports/'):
            sudo('zip -r /tmp/exports.zip ./')
    sudo('chown ubuntu /tmp/exports.zip')
    get('/tmp/exports.zip', './tmp/exports/exports.zip')
    sudo ('rm -rf /tmp/exports.zip', '.')
    sudo('chown -R deploy /srv/www/aesyntix/current/src/exports/')


@task
@parallel
def copyAppMmimImportServicesLogsToLocal():
    sudo('chown -R ubuntu /srv/www/aesyntix/shared/log/importServicesLogs')
    if not exists('/tmp/importServicesLogs.zip'):
        with cd('/srv/www/aesyntix/shared/log/importServicesLogs'):
            sudo('zip -r -y /tmp/importServicesLogs.zip ./')
    sudo('chown ubuntu /tmp/importServicesLogs.zip')
    get('/tmp/importServicesLogs.zip', './tmp/importServicesLogs/importServicesLogs.zip')
    sudo ('rm -rf /tmp/importServicesLogs.zip', '.')
    sudo('chown -R deploy /srv/www/aesyntix/shared/log/importServicesLogs')



@task
def checkAppMmim():
	#sudo('rm -rf  /srv/share/mmim/var/assets')
	#run('rm -rf /var/share')
    sudo('ls -lha /srv/share/mmim/var/assets/*')
    #sudo('mount -l |grep share')
    #sudo('chmod -R 777 /srv/share/mmim/var/assets')
	#run('curl -k https://localhost/site/login')
    #with cd('/srv/share/mmim/code/src/'):
    #    sudo('ln -snf  /srv/share/mmim/var/assets assets')
	    #sudo('ls -lha  assets')
		 
@task
def deployAppMmim():
    #sudo('rm -rf /srv/share/mmim/var/assets/*')
    with cd('/srv/share/mmim/code/'):
        run('git fetch --all')
        run('git checkout ' + env.deployBranch)
        run('git pull')
        
		


@task
@parallel
def installTheAppMmim():
    # Setup the config of the project ../mmim/etc/
    if not exists('/srv/share/mmim/etc/config/'):
        sudo('mkdir -p /srv/share/mmim/etc/config/')
    sudo('chown -R ubuntu:ubuntu /srv/share/mmim/etc/')
    with cd('/srv/share/mmim/etc/config/'):
        if not exists('main.php'):
            put('./config/mmim/' + env.setup + '/main.php', 'main.php')
        if not exists('console.php'):
            put('./config/mmim/' + env.setup + '/console.php', 'console.php')
        if not exists('cron.php'):
            put('./config/mmim/' + env.setup + '/cron.php', 'cron.php')
        if not exists('aws-config.php'):
            put('./config/mmim/' + env.setup + '/aws-config.php', 'aws-config.php')
    # Setup the code source of the project ../mmim/code/
    if not exists('/srv/share/mmim/code/.git'):
        sudo('mkdir -p /srv/share/mmim/')
        sudo('ssh-keyscan management.ascendro.de >> ~/.ssh/known_hosts')
        sudo('chown -R ubuntu:ubuntu /srv/share/mmim/')
        with cd('/srv/share/mmim/'):
            run(
                'git clone ssh://git@management.ascendro.de:22/ascendro05/ascendro32/ascendro19/synergo07/synergo23.git code')
    # Setup the var of the project ../mmim/etc/
    sudo('mkdir -p /srv/share/mmim/var/runtime')
    sudo('mkdir -p /srv/share/mmim/var/imgcache')
    sudo('mkdir -p /srv/share/mmim/var/assets')
    sudo('mkdir -p /srv/share/mmim/var/exports')
    sudo('mkdir -p /srv/share/mmim/var/importServicesLogs')
    sudo('chmod -R 770 /srv/share/mmim/var/')
    sudo('chown ubuntu:www-data /srv/share/mmim/var/')

    with cd('/srv/share/mmim/code/'):
        run('git fetch --all')
        run('git checkout ' + env.deployBranch)
        run('git pull')

        run('ln -snf  /srv/share/mmim/var/assets src/assets')
        run('ln -snf  /srv/share/mmim/var/imgcache src/imgcache')
        run('ln -snf  /srv/share/mmim/var/exports src/exports')
        run('ln -snf  /srv/share/mmim/var/runtime src/protected/runtime')
        run('ln -snf  /srv/share/mmim/var/importServicesLogs src/importServicesLogs')
        run('ln -snf  /srv/share/mmim/var/exports src/exports')
        sudo('ln -snf /srv/share/mmim/code/src/ /srv/www/current')
    # Run project connection with etc config using symlink
    with cd('/srv/share/mmim/code/src/protected/config'):
        if not exists('main.php'):
           run('ln -snf  /srv/share/mmim/etc/config/main.php main.php')
        if not exists('console.php'):
           run('ln -snf  /srv/share/mmim/etc/console.php console.php')
        if not exists('cron.php'):
           run('ln -snf /srv/share/mmim/etc/config/cron.php cron.php')
        if not exists('aws-config.php'):
           run('ln -snf /srv/share/mmim/etc/config/aws-config.php aws-config.php')



@task
@parallel
def copyAppMmimFilesFromLocal():
    sudo('mkdir -p /srv/share/mmim/var/imgcache')
    sudo('chmod -R 777 /srv/share/mmim/var/')
    #put('./tmp/imgcache', '/srv/share/mmim/var/imgcache')
    #put('./tmp/importServicesLogs', '/srv/share/mmim/var/importServicesLogs')
    put('./tmp/exports', '/srv/share/mmim/var/exports')
    sudo('chmod -R 770 /srv/share/mmim/var/')
    sudo('chown -R ubuntu:www-data /srv/share/mmim/var/')
    with cd('/srv/share/mmim/code/'):
        run('ln -snf  /srv/share/mmim/var/imgcache src/imgcache')



@task
@parallel
def copyAppMmimFilesFromLocal():
    sudo('mkdir -p /srv/share/mmim/var/imgcache')
    sudo('chmod -R 777 /srv/share/mmim/var/')
    #put('./tmp/imgcache', '/srv/share/mmim/var/imgcache')
    #put('./tmp/importServicesLogs', '/srv/share/mmim/var/importServicesLogs')
    put('./tmp/exports', '/srv/share/mmim/var/exports')
    sudo('chmod -R 770 /srv/share/mmim/var/')
    sudo('chown -R ubuntu:www-data /srv/share/mmim/var/')
    with cd('/srv/share/mmim/code/'):
        run('ln -snf  /srv/share/mmim/var/imgcache src/imgcache')

@task
@parallel
def fixImgCache():
    sudo('rm -rf /srv/share/mmim/code/imgcache')
    sudo('rm -rf /srv/www/current/imgcache/')
    sudo('rm -rf /srv/share/mmim/code/src/imagecache')
    sudo('rm -rf /srv/share/mmim/code/src/imgcache/imgcache/')
    sudo('rm -rf /srv/share/mmim/var/imgcache')
    sudo('rm -rf /srv/share/mmim/code/src/imgcache')
    sudo('mkdir -p /srv/share/mmim/code/src/imgcache')
    sudo('chmod 770  /srv/share/mmim/code/src/imgcache')
    sudo('chown -R ubuntu:www-data /srv/share/mmim/code/src/imgcache')

@task
@parallel
def fixUploadsDirs():
    #sudo('rm -rf /srv/share/mmim/code/uploads')
    sudo('mkdir -p /srv/share/mmim/var/uploads')
    sudo('ln -snf  /srv/share/mmim/var/uploads /srv/share/mmim/code/src/uploads')
    sudo('chmod 770  /srv/share/mmim/var/uploads')
    sudo('chown -R ubuntu:www-data  /srv/share/mmim/var/uploads')

@task
@parallel
def fixPhpSoap():
    #sudo('apt-get install -y php7.3-soap')
    sudo('service apache2 restart')


@task
@parallel
def logg(log):
  sudo('tail -f %s' % log)