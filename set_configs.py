import os
import sys

if __name__ == "__main__":
    # get informations
    if len(sys.argv) == 2 and len(sys.argv[1]) > 0:
        hostname = sys.argv[1]
    else:
        hostname = input("\n#####################################\nPlease type the desired server name \n(space separated if more than one, ex:'www.my_site.com my_site.com'): \n")
    if len(hostname) == 0:
        print("Error : name is empty")
        exit(-1)
    local_path = os.path.dirname(os.path.realpath(__file__))
    # replace vars and write files
    with open("virtual.conf", mode="r") as nginx_conf:
        nginx_data = nginx_conf.read().replace("[HOSTNAME]", hostname)
    with open("/etc/nginx/conf.d/virtual.conf", mode="w") as nginx_new_conf:
        nginx_new_conf.write(nginx_data)
    with open ("detect_label.conf", mode="r") as supervisor_conf:
        supervisor_data = supervisor_conf.read().replace("[USERNAME]", local_path)
    with open("/etc/supervisor/conf.d/detect_label.conf", mode="w") as supervisor_new_conf:
        supervisor_new_conf.write(supervisor_data)
