import Image from 'next/image';

export default function Header() {
    return (
        <header className="bg-gray-700 text-white p-4 flex items-center">
            <Image
                src="/dharmabot_logo.png"
                alt="DharmaBot Logo"
                width={40}
                height={40}
                className="mr-4"
            />
            <h1 className="text-2xl font-bold">DharmaBotUI</h1>
        </header>
    );
}