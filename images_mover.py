import subprocess
import argparse

def read_image_list(file_path):
    with open(file_path, "r") as f:
        image_list = f.read().splitlines()
    return image_list

def pull_save_as_tar_gz(image_list, save_tar, platforms):
    # Loop through the list and pull each image
    image_list_all_platforms = []
    for image_name in image_list:
        if platforms:
            for platform in platforms:
                platform_tag = platform.split("/")[-1]
                # Use subprocess to run the docker pull command and pull the image
                subprocess.run(["docker", "pull", "--platform", platform, image_name])
                subprocess.run(["docker", "tag", image_name, image_name + "-" + platform_tag])
                image_list_all_platforms.append(image_name + "-" + platform_tag)
        else:
            subprocess.run(["docker", "pull", image_name])
    if save_tar:
        # Use subprocess to run the docker save command and save the images to a tar file
        subprocess.run(["docker", "save", "-o", "image.tar"] + image_list if not platforms else ["docker", "save", "-o", "image.tar"] + image_list_all_platforms)

        # Compress the tar file using gzip
        subprocess.run(["gzip", "image.tar"])

# file_path is in tar.gz format
def tag_push_to_registry(image_list, registry_url, file_path="", project_name=None, platforms=None):
    if file_path != "":
        # Use subprocess to run the gunzip command and decompress the tar.gz file
        subprocess.run(["gunzip", file_path])

        # Get the name of the decompressed tar file
        tar_file = file_path[:-3]

        # Use subprocess to run the docker load command and load the images from the tar file
        subprocess.run(["docker", "load", "-i", tar_file])

    # Loop through the list of image names and tag and push each image to the specified registry
    for image_name in image_list:
        # Get the image name without the hostname
        image_name_without_hostname = image_name.split("/")[-1]

        # Tag the image with the specified registry URL, project name, and the image name without the hostname
        if project_name != None:
            tagged_image_name = registry_url + "/" + project_name + "/" + image_name_without_hostname
        else:
            tagged_image_name = registry_url + "/" + image_name_without_hostname
        manifest_all_platforms = []
        if platforms:
            for platform in platforms:
                platform_tag = platform.split("/")[-1]
                manifest_all_platforms.append(tagged_image_name + "-" + platform_tag)
                subprocess.run(["docker", "tag", image_name + "-" + platform_tag, tagged_image_name + "-" + platform_tag])
                subprocess.run(["docker", "push", tagged_image_name + "-" + platform_tag])
            subprocess.run(["docker", "manifest", "create", "--insecure", "--amend", tagged_image_name] + manifest_all_platforms)
            subprocess.run(["docker", "manifest", "push", "--insecure", tagged_image_name])
        else:
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
parser.add_argument('--platforms', nargs='+', help='List of architecture platforms to pull and push')
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
    pull_save_as_tar_gz(image_list, True, args.platforms)

# Pull the images without saving them to a tar file if the --pull switch is set
elif args.pull:
    pull_save_as_tar_gz(image_list, False, args.platforms)

# Tag and push the images to the registry if the --tag-push switch is set
if args.tag_push:
    if args.pull:
        tag_push_to_registry(image_list, args.registry_url, project_name=args.project_name, platforms=args.platforms)
    else:
        tag_push_to_registry(image_list, args.registry_url, "image.tar.gz", project_name=args.project_name, platforms=args.platforms)
