import './globals.css';
import type { Metadata } from 'next';
export const metadata: Metadata={title:'KIS AI Inspector',description:'Inspección inteligente de proyectos tecnológicos'};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="es"><body>{children}</body></html>}
