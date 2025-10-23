def cart_summary(request):
    # aman jika session belum ada
    items = request.session.get("cart_items", [])
    count = sum(i.get("qty", 0) for i in items)
    return {"cart_count": count}
