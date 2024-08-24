import './globals.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <title>DharmabotUI</title>
        <link rel="icon" href="/favicon.png" sizes="any" />
      </head>
      <body className="h-screen m-0 p-0">{children}</body>
    </html>
  )
}