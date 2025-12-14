import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Online Exam Proctoring',
  description: 'Real-time media capture and WebSocket infrastructure for online exam proctoring',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <style dangerouslySetInnerHTML={{
          __html: `
            * {
              margin: 0;
              padding: 0;
              box-sizing: border-box;
            }
            body {
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
              -webkit-font-smoothing: antialiased;
              -moz-osx-font-smoothing: grayscale;
              background-color: #ffffff;
            }
          `
        }} />
      </head>
      <body>{children}</body>
    </html>
  )
}
