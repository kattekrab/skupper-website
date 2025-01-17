#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

from transom.planocommands import *

site.output_dir = "docs"

@command
def generate_docs(owner="skupperproject", branch="main", output_dir="input/docs"):
    """
    Generate docs from the skupper-docs repo
    """

    check_program("antora")

    playbook_in = get_absolute_path("scripts/docs-playbook.yaml.in")
    output_dir = get_absolute_path(output_dir)

    with working_dir():
        content = read(playbook_in)
        content = content.replace("@branch@", branch)
        content = content.replace("@owner@", owner)
        playbook = write("docs-playbook.yaml", content)

        run(f"antora --fetch {playbook}")

        for path in find("build", "*.html"):
            move(path, f"{path}.in")

        copy("build/skupper/latest/console", output_dir)
        copy("build/skupper/latest/overview", output_dir)
        copy("build/skupper/latest/cli", output_dir)
        copy("build/skupper/latest/cli-reference", output_dir)
        copy("build/skupper/latest/cli-podman", output_dir)
        copy("build/skupper/latest/declarative", output_dir)
        copy("build/skupper/latest/troubleshooting", output_dir)
        copy("build/skupper/latest/policy", output_dir)
        copy("build/skupper/latest/operator", output_dir)
        copy("build/skupper/latest/_images", output_dir + "/_images")

@command
def generate_examples(output_file="input/examples/index.html.in"):
    """
    Generate the example index using metadata in scripts/examples.yaml
    """

    examples_data = read_yaml("scripts/examples.yaml")
    github_data = http_get_json("https://api.github.com/orgs/skupperproject/repos?per_page=100")
    repos = dict()

    for repo_data in github_data:
        repos[repo_data["name"]] = repo_data

    output_file = get_absolute_path(output_file)
    out = list()

    out.append("---")
    out.append("title: Examples")
    out.append("extra_headers: <link rel=\"stylesheet\" href=\"index.css\" type=\"text/css\" async=\"async\"/><link rel=\"stylesheet\" href=\"https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@48,400,0,0\"/>")
    out.append("---")

    out.append("<h1>Skupper examples</h1>")
    out.append("")
    out.append("<p>These examples provide step-by-step instructions to install and use Skupper for common multi-cluster and edge deployment scenarios.</p>")

    for category in examples_data["categories"]:
        category_title = category["title"]
        category_id = category_title.lower().replace(" ", "-")
        category_description = category.get("description")

        out.append(f"<h2 id=\"{category_id}\">{category_title}</h2>")
        out.append("")

        if category_description is not None:
            out.append(f"<p>{category_description}</p>")
            out.append("")

        out.append("<div class=\"examples\">")
        out.append("")

        for example_data in category["examples"]:
            name = example_data["name"]
            title = example_data["title"]

            try:
                repo_data = repos[name]
            except:
                description = example_data.get("description")
                url = example_data.get("url")
            else:
                description = example_data.get("description", repo_data["description"])
                url = example_data.get("url", repo_data["html_url"])

            out.append("<div>")
            out.append(f"<h3><a href=\"{url}\">{title}</a></h3>")
            out.append(f"<p>{description}</p>")
            out.append("<nav class=\"inline-links\">")
            out.append(f"<a href=\"{url}\"><span class=\"fab fa-github fa-lg\"></span> Example</a>")

            if "video_url" in example_data:
                video_url = example_data["video_url"]
                out.append(f"<a href=\"{video_url}\"><span class=\"fab fa-youtube fa-lg\"></span> Video</a>")

            out.append("</nav>")
            out.append("</div>")

        out.append("</div>")
        out.append("")

    write(output_file, "\n".join(out))

@command
def test():
    render()
    check_links()
    check_files()

    with temp_dir() as d:
        with working_env(HOME=d):
            run("cat docs/install.sh | sh", shell=True)

        generate_docs(output_dir=d)
