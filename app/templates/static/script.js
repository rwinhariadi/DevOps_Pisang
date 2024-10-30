// Fungsi untuk menampilkan pratinjau gambar dan langsung mengirim form setelah gambar dipilih
function previewAndSubmit (event) {
  const fileInput = event.target
  const reader = new FileReader()
  const iconContainer = document.getElementById('icon-container')
  const uploadedImage = document.getElementById('uploaded-image')

  // Tampilkan pratinjau gambar dan ganti ikon cloud
  if (fileInput.files && fileInput.files[0]) {
    reader.onload = function () {
      uploadedImage.src = reader.result
      uploadedImage.style.display = 'block'
      iconContainer.style.display = 'none' // Sembunyikan ikon setelah upload
    }
    reader.readAsDataURL(fileInput.files[0])

    // Membuat FormData dan menambahkan file yang diunggah
    const formData = new FormData()
    formData.append('file', fileInput.files[0])

    // Mengirim data unggahan ke server dan menampilkan hasil
    fetch('/upload', {
      method: 'POST',
      body: formData
    })
      .then((response) => response.json())
      .then((result) => {
        if (result.error) {
          throw new Error(result.error)
        }

        // Menentukan warna berdasarkan status kematangan
        const color = result.prediction === 'Matang' ? 'Kuning' : 'Hijau'

        // Tampilkan hasil prediksi
        document.getElementById('color').innerText = color
        document.getElementById('result').innerText = result.prediction
      })
      .catch((error) => {
        console.error('Error:', error)
        document.getElementById('result').innerText = 'Gagal memproses gambar'
        document.getElementById('color').innerText = '-' // Reset warna jika gagal
      })
  } else {
    console.error('No file selected')
  }
}

// Menambahkan event listener untuk file input
document.getElementById('file-input').addEventListener('change', previewAndSubmit)
