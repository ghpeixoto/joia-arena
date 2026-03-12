import type { Metadata } from 'next'
import './globals.css'

// Configuração dos metadados e do ícone da aba
export const metadata: Metadata = {
  title: 'JoIA - Arena de Inteligência',
  description: 'Sua arena de IA para produzir mais.',
  icons: {
    icon: '/imagem.png', // Aponta para a imagem que você colocou na pasta public
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      {/* Adicionamos a classe 'dark' para garantir que o Tailwind funcione bem no modo escuro se necessário */}
      <body className="dark">{children}</body>
    </html>
  )
}