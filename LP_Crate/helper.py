import os
import subprocess
import logging
import hashlib
from urllib.parse import quote

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitURL:
    def __init__(self, repo_path=".", remote_name="origin", branch_name=None):
        self.repo_path = os.path.abspath(repo_path)  # Normalize the path
        self.remote_name = remote_name
        self.branch_name = branch_name
        self.remote_url = self._get_remote_url()
        self.repo_root = self._get_repo_root()
        self.commit_hash = self._get_commit_hash()
        if not self.branch_name:
            self.branch_name = self._get_branch_name()

    def _get_remote_url(self):
        remote_url = subprocess.check_output(
            ["git", "-C", self.repo_path, "remote", "get-url", self.remote_name],
            text=True
        ).strip()
        if remote_url.startswith("git@github.com:"):
            remote_url = remote_url.replace("git@github.com:", "https://github.com/")
        if remote_url.endswith(".git"):
            remote_url = remote_url[:-4]
        return remote_url

    def _get_repo_root(self):
        return subprocess.check_output(
            ["git", "-C", self.repo_path, "rev-parse", "--show-toplevel"],
            text=True
        ).strip()

    def _get_branch_name(self):
        return subprocess.check_output(
            ["git", "-C", self.repo_path, "rev-parse", "--abbrev-ref", "HEAD"],
            text=True
        ).strip()

    def _get_commit_hash(self):
        return subprocess.check_output(
            ["git", "-C", self.repo_path, "rev-parse", "HEAD"],
            text=True
        ).strip()

    def get(self, local_path):
        abs_path = os.path.abspath(os.path.join(self.repo_path, local_path))
        rel_path = os.path.relpath(abs_path, self.repo_root)
        encoded_path = quote(rel_path)
        latest_url = f"{self.remote_url}/blob/{self.branch_name}/{encoded_path}"
        permalink_url = f"{self.remote_url}/blob/{self.commit_hash}/{encoded_path}"
        return {
            "latest_url": latest_url,
            "permalink_url": permalink_url,
            "commit_hash": self.commit_hash
        }

    def get_size(self, local_path):
        abs_path = os.path.abspath(os.path.join(self.repo_path, local_path))
        if not os.path.isfile(abs_path):
            raise FileNotFoundError(f"{abs_path} is not a file.")
        size_bytes = os.path.getsize(abs_path)
        size_kb = size_bytes / 1024
        return f"{size_kb:.2f}"
    

    def get_previous_commit_hash(self):
        # Find the second most recent commit with message "auto update"
        log_output = subprocess.check_output(
            ["git", "-C", self.repo_path, "log", "--grep=auto update", "--pretty=format:%H"],
            text=True
        ).strip().splitlines()
        if len(log_output) < 2:
            raise ValueError("Less than two 'auto update' commits found.")
        return log_output[1]

    def get_previous(self, local_path):
        previous_hash = self.get_previous_commit_hash()
        abs_path = os.path.abspath(os.path.join(self.repo_path, local_path))
        rel_path = os.path.relpath(abs_path, self.repo_root)
        encoded_path = quote(rel_path)
        # Check if file exists at previous commit
        try:
            subprocess.check_output(
                ["git", "-C", self.repo_path, "show", f"{previous_hash}:{rel_path}"],
                stderr=subprocess.DEVNULL
            )
            permalink_url = f"{self.remote_url}/blob/{previous_hash}/{encoded_path}"
            return {
                "permalink_url": permalink_url,
                "commit_hash": previous_hash,
                "exists": True
            }
        except subprocess.CalledProcessError:
            # Fallback to current file
            permalink_url = f"{self.remote_url}/blob/{self.commit_hash}/{encoded_path}"
            return {
                "permalink_url": permalink_url,
                "commit_hash": self.commit_hash,
                "exists": False
            }

    def get_size_at_commit(self, local_path, commit_hash):
        rel_path = os.path.relpath(
            os.path.abspath(os.path.join(self.repo_path, local_path)),
            self.repo_root
        )
        try:
            content = subprocess.check_output(
                ["git", "-C", self.repo_path, "show", f"{commit_hash}:{rel_path}"],
                stderr=subprocess.DEVNULL
            )
            size_kb = len(content) / 1024
            return f"{size_kb:.2f}"
        except subprocess.CalledProcessError:
            raise FileNotFoundError(f"{rel_path} does not exist at commit {commit_hash}")

    def get_file_hash(self, local_path, which="current"):
        """
        Return SHA-256 hash of the file contents for the specified commit state.
        which: "current" for working directory file, "previous" for the second most recent 'auto update' commit.
        Returns None if the file does not exist.
        """
        try:
            if which == "current":
                abs_path = os.path.abspath(os.path.join(self.repo_path, local_path))
                if not os.path.isfile(abs_path):
                    return None
                with open(abs_path, "rb") as f:
                    content = f.read()
            elif which == "previous":
                previous_hash = self.get_previous_commit_hash()
                rel_path = os.path.relpath(
                    os.path.abspath(os.path.join(self.repo_path, local_path)),
                    self.repo_root
                )
                try:
                    content = subprocess.check_output(
                        ["git", "-C", self.repo_path, "show", f"{previous_hash}:{rel_path}"],
                        stderr=subprocess.DEVNULL
                    )
                except subprocess.CalledProcessError:
                    return None
            else:
                return None
            return hashlib.sha256(content).hexdigest()
        except Exception:
            return None

        return hashlib.sha256(content).hexdigest()
    
    def get_commit_info_for_file(self, local_path):
        """
        Returns the latest commit hash that modified the given file
        and a link to the GitHub page for that commit.
        """
        abs_path = os.path.abspath(os.path.join(self.repo_path, local_path))
        rel_path = os.path.relpath(abs_path, self.repo_root)

        try:
            commit_hash = subprocess.check_output(
                ["git", "-C", self.repo_path, "log", "-n", "1", "--pretty=format:%H", "--", rel_path],
                text=True
            ).strip()

            commit_url = f"{self.remote_url}/commit/{commit_hash}"
            return {
                "commit_hash": commit_hash,
                "commit_url": commit_url
            }

        except subprocess.CalledProcessError:
            raise ValueError(f"Could not retrieve commit info for file: {rel_path}")

    def get_commit_date(self):
        """
        Returns the ISO 8601 timestamp of the current commit.
        Format: YYYY-MM-DDTHH:MM:SS+00:00
        """
        try:
            commit_date = subprocess.check_output(
                ["git", "-C", self.repo_path, "show", "-s", "--format=%cI", self.commit_hash],
                text=True
            ).strip()
            return commit_date
        except subprocess.CalledProcessError:
            raise ValueError("Could not retrieve commit date.")

    def get_current_commit(self):
        """
        Returns the URL for the latest commit of the repository.
        Format: https://github.com/owner/repo/commit/full_commit_hash
        """
        return f"{self.remote_url}/commit/{self.commit_hash}"

if __name__ == "__main__":
    # Example usage
    url_gen = GitURL(
        repo_path="/Users/eller/Projects/CoastSat_Implementation/CoastSat"
    )
    result = url_gen.get("/Users/eller/Projects/CoastSat_Implementation/CoastSat/linear_models.ipynb")
    print("Latest URL:     ", result["latest_url"])
    print("Permalink URL:  ", result["permalink_url"])
    print("Commit Hash:    ", result["commit_hash"])
    size = url_gen.get_size("linear_models.ipynb")
    print("File Size:      ", size)
   

    previous = url_gen.get_previous("linear_models.ipynb")
    print("Previous URL:   ", previous["permalink_url"])
    print("Previous Hash:  ", previous["commit_hash"])
    previous_size = url_gen.get_size_at_commit("linear_models.ipynb", previous["commit_hash"])
    print("Previous Size:  ", previous_size)

    commit_info = url_gen.get_commit_info_for_file("linear_models.ipynb")["commit_url"]
    print("Commit Info:    ", commit_info)