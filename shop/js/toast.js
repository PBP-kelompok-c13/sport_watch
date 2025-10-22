function showToast(message, type = 'normal') {
    const toast = document.getElementById('toast');
    const text = document.getElementById('toast-text');

    if (!toast || !text) return;

    // reset style
    toast.className = "fixed bottom-6 right-6 hidden opacity-0 transform translate-y-5 transition-all duration-300 ease-in-out z-50 max-w-sm w-full sm:w-80 px-5 py-4 rounded-lg shadow-lg text-sm font-medium";

    // atur warna berdasarkan tipe
    if (type === 'success') {
        toast.classList.add('bg-green-100', 'text-green-800', 'border', 'border-green-300');
    } else if (type === 'error') {
        toast.classList.add('bg-red-100', 'text-red-700', 'border', 'border-red-300');
    } else {
        toast.classList.add('bg-slate-100', 'text-slate-800', 'border', 'border-slate-300');
    }

    // set isi pesan
    text.textContent = message;

    // tampilkan toast (animasi muncul)
    toast.classList.remove('hidden', 'opacity-0', 'translate-y-5');
    toast.classList.add('opacity-100', 'translate-y-0');

    // sembunyikan setelah 3 detik
    setTimeout(() => {
        toast.classList.remove('opacity-100', 'translate-y-0');
        toast.classList.add('opacity-0', 'translate-y-5');

        // tunggu animasi keluar dulu sebelum hide
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 300);
    }, 3000);
}
