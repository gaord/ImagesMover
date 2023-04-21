import subprocess
import argparse

def read_image_list(file_path):
    with open(file_path, "r") as f:
        image_list = f.read().splitlines()
    return image_list

def pull_save_as_tar_gz(image_list, save_tar):
    # Loop through the list and pull each image
    for image_name in image_list:
        subprocess.run(["docker", "pull", image_name])
    if save_tar:
        print("Saving images to image.tar file")
        # Use subprocess to run the docker save command and save the images to a tar file
        subprocess.run(["docker", "save", "-o", "image.tar"] + image_list)
        print("Compressing image.tar file")
        # Compress the tar file using gzip
        subprocess.run(["gzip", "image.tar"])

# file_path is in tar.gz format
def tag_push_to_registry(image_list, registry_url, file_path="", project_name=None):
    if file_path != "":
        print("Decompressing image.tar.gz file")
        # Use subprocess to run the gunzip command and decompress the tar.gz file
        subprocess.run(["gunzip", file_path])

        # Get the name of the decompressed tar file
        tar_file = file_path[:-3]
        print("Loading images from " + tar_file + " file")
        # Use subprocess to run the docker load command and load the images from the tar file
        subprocess.run(["docker", "load", "-i", tar_file])
        with open(tar_file, "rb") as tar:
            determined_image_list = [image.tags[0] for image in client.images.load(tar) if hasattr(image, 'tags') and len(image.tags) > 0]
    else:
        determined_image_list = image_list
    # Loop through the list of image names and tag and push each image to the specified registry
    for image_name in determined_image_list:
        # Get the image name without the hostname
        image_name_without_hostname = image_name.split("/")[-1]

        # Tag the image with the specified registry URL, project name, and the image name without the hostname
        if project_name != None:
            tagged_image_name = registry_url + "/" + project_name + "/" + image_name_without_hostname
        else:
            tagged_image_name = registry_url + "/" + image_name_without_hostname
        subprocess.run(["docker", "tag", image_name, tagged_image_name])

        # Push the tagged image to the registry
        subprocess.run(["docker", "push", tagged_image_name])

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--tag-push", action="store_true", help="Tag and push the images to the registry")
parser.add_argument("--pull", action="store_true", help="Pull the images without saving them to a tar file")
parser.add_argument("--pull-save", action="store_true", help="Pull the images and save them to a tar file")
parser.add_argument("--project-name", type=str, help="Specify the project name for pushing the images to the registry")
parser.add_argument("--image-list-file", type=str, help="Specify the file path for reading the image list")
parser.add_argument("--registry-url", type=str, help="Specify local docker image registry to push to")
args = parser.parse_args()

# Check if the --image-list-file argument is set
if not args.image_list_file and (args.pull or args.pull_save):
    parser.error("--image-list-file is required with pulling operation")

image_list = []
if args.image_list_file:
# Read the image list from file
    image_list = read_image_list(args.image_list_file)

if not args.registry_url and args.tag_push:
    parser.error("--registry-url is required with pushing operation")

# Pull the images and save them to a tar file if the --pull-save switch is set
if args.pull_save:
    pull_save_as_tar_gz(image_list, True)

# Pull the images without saving them to a tar file if the --pull switch is set
elif args.pull:
    pull_save_as_tar_gz(image_list, False)

# Tag and push the images to the registry if the --tag-push switch is set
if args.tag_push:
    if args.pull:
        tag_push_to_registry(image_list, args.registry_url, project_name=args.project_name)
    else:
        tag_push_to_registry(image_list, args.registry_url, "image.tar.gz", project_name=args.project_name)
