import Image from 'next/image';
import Link from 'next/link';

export function Logo({ size = 'default' }: { size?: 'small' | 'default' | 'large' }) {
  const dimensions = {
    small: { width: 32, height: 32 },
    default: { width: 40, height: 40 },
    large: { width: 56, height: 56 },
  };

  const { width, height } = dimensions[size];

  return (
    <Link href="/" className="flex items-center space-x-3">
      <div className="relative" style={{ width, height }}>
        <Image
          src="/hawk-logo.jpg"
          alt="Market Hawk Eye Logo"
          width={width}
          height={height}
          className="object-contain"
          priority
        />
      </div>
      <h1 className={`font-bold text-text-primary ${size === 'small' ? 'text-lg' : 'text-2xl'}`}>
        Markey HawkEye
      </h1>
    </Link>
  );
}
