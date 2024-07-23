const fs = require('fs')
const path = require('path')
const { exec } = require('child_process')

const directoryPath = './' // Replace with the path to your directory

async function runFilesWithDelay(directory, delay) {
  const files = fs.readdirSync(directory)

  for (const file of files) {
    const filePath = path.join(directory, file)

    if (path.extname(file) === '.js') {
      await runFile(filePath)
      await delayExecution(delay)
    }
  }
}

function runFile(filePath) {
  return new Promise((resolve, reject) => {
    const childProcess = exec(`node ${filePath}`, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error executing ${filePath}: ${error.message}`)
        reject(error)
      } else {
        console.log(`Output of ${filePath} (stdout):\n${stdout}`)
        console.error(`Output of ${filePath} (stderr):\n${stderr}`)
        resolve(stdout)
      }
    })

    // Forward child process stdout and stderr to parent process
    childProcess.stdout.pipe(process.stdout)
    childProcess.stderr.pipe(process.stderr)
  })
}

function delayExecution(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

// Usage
runFilesWithDelay(directoryPath, 10 * 1000)
  .then(() => console.log('All files executed.'))
  .catch((err) => console.error('Error executing files:', err))
