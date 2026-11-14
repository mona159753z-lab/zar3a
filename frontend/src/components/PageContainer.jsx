export default function PageContainer({ children, className = '' }) {
  return (
    <main
      className={`mx-auto w-full max-w-7xl space-y-5 overflow-x-hidden px-4 pb-16 pt-24 sm:space-y-6 sm:px-6 sm:pt-28 lg:px-8 ${className}`}
    >
      {children}
    </main>
  )
}