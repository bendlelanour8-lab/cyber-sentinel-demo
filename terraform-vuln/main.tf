provider "google" {
  project = "mon-projet-demo"
  region  = "europe-west1"
}

resource "google_storage_bucket" "data" {
  name                        = "pfa-demo-bucket-12345"
  location                    = "EU"
  uniform_bucket_level_access = false
}

resource "google_storage_bucket_iam_member" "public" {
  bucket = google_storage_bucket.data.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

resource "google_compute_firewall" "ssh_open" {
  name    = "allow-ssh-all"
  network = "default"
  allow {
    protocol = "tcp"
    ports    = ["22", "3389"]
  }
  source_ranges = ["0.0.0.0/0"]
}
