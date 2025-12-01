import * as React from 'react'
import Link from 'next/link'
import EnvCard from './cards/envcard'

export async function Header() {
  return (
    <header className="sticky top-0 z-50 flex items-center justify-between w-full h-16 px-4 border-b shrink-0 bg-white backdrop-blur-sm">
      <div className="flex items-center gap-4">
        <EnvCard />
        <Link href="/" rel="nofollow" className="text-xl font-bold text-gray-900 hover:text-gray-700 transition-colors">
          Data Analysis AI
        </Link>
      </div>
    </header>
  )
}
