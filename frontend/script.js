console.log('Script.js loaded successfully')

const METRICS_ENDPOINT = 'http://localhost:8080/metrics/frontend'

function sendMetric (metricName, value, labels = {}) {
  fetch(METRICS_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ metric: metricName, value, labels })
  }).catch(error => {
    console.error('Failed to send metric:', error)
  })
}

window.addEventListener('load', () => {
  const [navigationTiming] = performance.getEntriesByType('navigation')

  if (navigationTiming) {
    const pageLoadTime = navigationTiming.loadEventEnd - navigationTiming.startTime
    console.log(`Page Load Time: ${pageLoadTime}ms`)

    sendMetric('page_load_time', pageLoadTime)
  } else {
    console.warn('PerformanceNavigationTiming is not supported')
  }
})

const currentPage = window.location.pathname

if (currentPage.includes('index.html') || currentPage === '/') {
  console.log('Index page detected')

  const fileInput = document.getElementById('file-input')

  if (fileInput) {
    fileInput.addEventListener('change', event => {
      const reader = new FileReader()
      const iconContainer = document.getElementById('icon-container')
      const uploadedImage = document.getElementById('uploaded-image')

      if (event.target.files && event.target.files[0]) {
        reader.onload = () => {
          uploadedImage.src = reader.result
          uploadedImage.style.display = 'block'
          iconContainer.style.display = 'none'
        }
        reader.readAsDataURL(event.target.files[0])

        const formData = new FormData()
        formData.append('file', event.target.files[0])

        const startTime = performance.now()

        fetch('http://localhost:8080/upload', {
          method: 'POST',
          body: formData
        })
          .then(response => {
            const latency = performance.now() - startTime
            console.log(`API Latency (upload): ${latency}ms`)

            sendMetric('api_latency', latency, { endpoint: '/upload' })

            if (!response.ok) {
              throw new Error(`Gagal memproses gambar. Status: ${response.status}`)
            }
            return response.json()
          })
          .then(result => {
            if (result.error) {
              throw new Error(result.error)
            }

            const color = result.prediction === 'Matang' ? 'Kuning' : 'Hijau'

            document.getElementById('color').innerText = color
            document.getElementById('result').innerText = result.prediction

            addToHistory({
              image: uploadedImage.src,
              color,
              status: result.prediction
            })

            sendMetric('file_uploads', 1)
          })
          .catch(error => {
            console.error('Error:', error)
            document.getElementById('result').innerText = 'Gagal memproses gambar'
            document.getElementById('color').innerText = '-'
          })
      } else {
        console.error('No file selected')
      }
    })
  } else {
    console.warn('File input element not found on index.html')
  }
}

if (currentPage.includes('history.html')) {
  console.log('History page detected')

  const historyCards = document.getElementById('history-cards')

  if (!historyCards) {
    console.error('Element with ID "history-cards" not found')
  } else {
    console.log('Element "history-cards" ditemukan')

    historyCards.innerHTML = ''

    const startTime = performance.now()
    fetch('http://localhost:8080/get-history')
      .then(response => {
        console.log('Fetch response:', response)

        const latency = performance.now() - startTime
        console.log(`API Latency (get-history): ${latency}ms`)

        sendMetric('api_latency', latency, { endpoint: '/get-history' })

        if (!response.ok) {
          throw new Error('Failed to fetch history data')
        }
        return response.json()
      })
      .then(data => {
        console.log('Data fetched:', data)

        const totalCards = Math.max(data.length, 10)
        for (let i = 0; i < totalCards; i++) {
          const card = document.createElement('div')
          card.classList.add('history-card')

          if (data[i]) {
            card.innerHTML = `
              <img src='${data[i].image}' alt='Uploaded Image' />
              <p>Warna: ${data[i].color}</p>
              <p>Status: ${data[i].status}</p>
            `
          } else {
            card.innerHTML = `
              <p style='color: #ccc; font-size: 1.2em; margin: auto;'>Kosong</p>
            `
          }

          historyCards.appendChild(card)
        }
        
        sendMetric('history_cards_displayed', totalCards)
      })
      
      .catch(error => {
        console.error('Error fetching history:', error)
      })
  }
}

function addToHistory (item) {
  const historyCards = document.getElementById('history-cards')
  if (!historyCards) {
    console.warn('History container not found, skipping addition')
    return
  }

  const card = document.createElement('div')
  card.classList.add('history-card')
  card.innerHTML = `
    <img src='${item.image}' alt='Uploaded Image' />
    <p>Warna: ${item.color}</p>
    <p>Status: ${item.status}</p>
  `
  historyCards.appendChild(card)
}
