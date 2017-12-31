# Wire Django
A website inspired by twitter made using Django

## Prerequisites
1. Vagrant >= 2.0 https://www.vagrantup.com/downloads.html
2. A version of VirtualBox supported by your version of vagrant. For vagrant 2.0, use VirtualBox 5.1 https://www.virtualbox.org/wiki/Download_Old_Builds_5_1

## Getting the site running
Install the vagrant-vbguest plugin `vagrant plugin install vagrant-vbguest`
`cd vagrant` and `vagrant up`
If this is your first `vagrant up`, go make a cup of tea. This will take a while
Once the `vagrant up` has finished, `vagrant ssh` into your box
`cd /django/wire`
`python3 manage.py runserver`
Now you should be able to access the site at `localhost:8080`

