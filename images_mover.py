import subprocess
import argparse

# List of Docker image to be moved to the local registry
#image_list = ["quay.io/prometheus/node-exporter:v1.3.1", "docker.io/grafana/loki:2.4.0", "docker.io/grafana/promtail:2.4.0", "quay.io/ceph/haproxy:2.3", "quay.io/ceph/keepalived:2.1.5", "docker.io/maxwo/snmp-notifier:v1.2.1"]
image_list = ["quay.io/prometheus/alertmanager:v0.23.0", "quay.io/prometheus/prometheus:v2.33.4", "quay.io/ceph/ceph-grafana:8.3.5"]
# Local Registry URL
registry_url = "10.123.123.123:5000"


def pull_save_as_tar_gz(image_list, save_tar):
    # Loop through the list and pull each image
    for image_name in image_list:
        subprocess.run(["docker", "pull", image_name])
    if save_tar:
        # Use subprocess to run the docker save command and save the images to a tar file
        subprocess.run(["docker", "save", "-o", "image.tar"] + image_list)

        # Compress the tar file using gzip
        subprocess.run(["gzip", "image.tar"])

# file_path is in tar.gz format
def tag_push_to_registry(image_list, registry_url, file_path):
    if file_path != "":
        # Use subprocess to run the gunzip command and decompress the tar.gz file
        subprocess.run(["gunzip", file_path])

        # Get the name of the decompressed tar file
        tar_file = file_path[:-3]

        # Use subprocess to run the docker load command and load the images from the tar file
        subprocess.run(["docker", "load", "-i", tar_file])

    # Loop through the list of image names and tag and push each image to the specified registry
    for image_name in image_list:
        # Tag the image with the specified registry URL
        tagged_image_name = registry_url + "/" + image_name.split("/")[-1]
        subprocess.run(["docker", "tag", image_name, tagged_image_name])

        # Push the tagged image to the registry
        subprocess.run(["docker", "push", tagged_image_name])

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--tag-push", action="store_true", help="Tag and push the images to the registry")
parser.add_argument("--pull", action="store_true", help="Pull the images without saving them to a tar file")
parser.add_argument("--pull-save", action="store_true", help="Pull the images and save them to a tar file")
args = parser.parse_args()

# Pull the images and save them to a tar file if the --pull-save switch is set
if args.pull_save:
    pull_save_as_tar_gz(image_list, True)

# Pull the images without saving them to a tar file if the --pull switch is set
elif args.pull:
    pull_save_as_tar_gz(image_list, False)

# Tag and push the images to the registry if the --tag-push switch is set
elif args.tag_push:
    if args.pull:
        tag_push_to_registry(image_list, registry_url, "")
    else:
        tag_push_to_registry(image_list, registry_url, "image.tar.gz")


# Print an error message if no switches are set
else:
    print("Error: You must specify at least one switch (--tag-push, --pull, or --pull-save).")