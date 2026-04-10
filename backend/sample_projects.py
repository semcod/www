"""Sample projects from different git systems for testing and demonstration."""

SAMPLE_PROJECTS = [
    # GitHub projects
    {
        "url": "https://github.com/torvalds/linux",
        "platform": "github",
        "name": "torvalds/linux",
        "description": "Linux kernel source tree",
    },
    {
        "url": "https://github.com/python/cpython",
        "platform": "github",
        "name": "python/cpython",
        "description": "CPython main branch",
    },
    {
        "url": "https://github.com/facebook/react",
        "platform": "github",
        "name": "facebook/react",
        "description": "React JavaScript library",
    },
    {
        "url": "https://github.com/golang/go",
        "platform": "github",
        "name": "golang/go",
        "description": "Go programming language",
    },
    # GitLab projects
    {
        "url": "https://gitlab.com/gitlab-org/gitlab",
        "platform": "gitlab",
        "name": "gitlab-org/gitlab",
        "description": "GitLab CE/EE",
    },
    {
        "url": "https://gitlab.com/gitlab-org/terraform-stages/gitlab-terraform-gcp-example",
        "platform": "gitlab",
        "name": "gitlab-org/terraform-stages/gitlab-terraform-gcp-example",
        "description": "Terraform GCP example",
    },
    # Bitbucket projects
    {
        "url": "https://bitbucket.org/atlassian/python-bitbucket",
        "platform": "bitbucket",
        "name": "atlassian/python-bitbucket",
        "description": "Python Bitbucket API client",
    },
    {
        "url": "https://bitbucket.org/atlassianlabs/coveralls-python",
        "platform": "bitbucket",
        "name": "atlassianlabs/coveralls-python",
        "description": "Coveralls Python client",
    },
    # Additional diverse projects
    {
        "url": "https://github.com/microsoft/vscode",
        "platform": "github",
        "name": "microsoft/vscode",
        "description": "Visual Studio Code",
    },
    {
        "url": "https://github.com/rust-lang/rust",
        "platform": "github",
        "name": "rust-lang/rust",
        "description": "Rust programming language",
    },
]

def get_sample_projects():
    """Return list of sample projects for scanning."""
    return SAMPLE_PROJECTS
