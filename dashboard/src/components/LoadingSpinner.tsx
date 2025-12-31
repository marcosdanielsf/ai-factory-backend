export function LoadingSpinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
  }

  return (
    <div className="flex items-center justify-center p-8">
      <div
        className={`${sizeClasses[size]} border-gray-200 border-t-blue-600 rounded-full animate-spin`}
      />
    </div>
  )
}

export function LoadingCard() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
      <div className="grid grid-cols-2 gap-4">
        <div className="h-12 bg-gray-100 rounded"></div>
        <div className="h-12 bg-gray-100 rounded"></div>
        <div className="h-12 bg-gray-100 rounded"></div>
        <div className="h-12 bg-gray-100 rounded"></div>
      </div>
      <div className="h-8 bg-gray-100 rounded mt-4"></div>
    </div>
  )
}
