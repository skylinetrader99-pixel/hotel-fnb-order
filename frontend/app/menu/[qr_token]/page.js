"use client";

import { use, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

export default function MenuPage({ params }) {
  const { qr_token } = use(params);
  const router = useRouter();

  const [data, setData] = useState(null);
  const [cart, setCart] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    async function loadMenu() {
      try {
        setLoading(true);
        setError("");

        const res = await fetch(`http://127.0.0.1:8000/menu/${qr_token}`);
        if (!res.ok) {
          throw new Error("Failed to fetch menu");
        }

        const json = await res.json();
        setData(json);
      } catch (err) {
        setError(err.message || "Something went wrong");
      } finally {
        setLoading(false);
      }
    }

    loadMenu();
  }, [qr_token]);

  function addToCart(item) {
    setCart((prev) => {
      const existing = prev.find((cartItem) => cartItem.id === item.id);

      if (existing) {
        return prev.map((cartItem) =>
          cartItem.id === item.id
            ? { ...cartItem, qty: cartItem.qty + 1 }
            : cartItem
        );
      }

      const price =
        item.is_promotion && item.promo_price ? item.promo_price : item.price;

      return [
        ...prev,
        {
          id: item.id,
          name_th: item.name_th,
          name_en: item.name_en,
          price,
          qty: 1,
        },
      ];
    });
  }

  function increaseQty(id) {
    setCart((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, qty: item.qty + 1 } : item
      )
    );
  }

  function decreaseQty(id) {
    setCart((prev) =>
      prev
        .map((item) =>
          item.id === id ? { ...item, qty: item.qty - 1 } : item
        )
        .filter((item) => item.qty > 0)
    );
  }
async function placeOrder() {
  if (cart.length === 0) {
    alert("Cart is empty");
    return;
  }

  try {
    setSubmitting(true);
    setSuccessMessage("");

    const payload = {
      qr_token: qr_token,
      items: cart.map((item) => ({
        menu_item_id: item.id,
        qty: item.qty,
      })),
    };

    const res = await fetch("http://127.0.0.1:8000/orders", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || "Failed to place order");
    }

    const result = await res.json();

    setCart([]);
    setSuccessMessage(
    `Order placed successfully. Order ID: ${result.order.order_id}`
    );

    setTimeout(() => {
    router.push(`/order/${result.order.order_id}`);
    }, 1000);
    
  } catch (err) {
    alert(err.message || "Something went wrong");
  } finally {
    setSubmitting(false);
  }
}

  const totalAmount = useMemo(() => {
    return cart.reduce((sum, item) => sum + item.price * item.qty, 0);
  }, [cart]);

  if (loading) {
    return <main className="p-6">Loading menu...</main>;
  }

  if (error) {
    return <main className="p-6 text-red-600">Error: {error}</main>;
  }

  return (
    <main className="min-h-screen bg-gray-100 p-6 pb-40">
      <div className="mx-auto max-w-3xl">
        <div className="mb-6 rounded-2xl bg-white p-6 shadow">
          <h1 className="text-2xl font-bold text-gray-900">Room Service Menu</h1>
          {successMessage && (
  <div className="mb-6 rounded-2xl bg-green-100 p-4 text-green-800 shadow">
    {successMessage}
  </div>
)}
          <p className="mt-2 text-gray-600">
            Room: {data.room.room_number} | Floor: {data.room.floor} | Building: {data.room.building}
          </p>
        </div>

        <div className="grid gap-4">
          {data.menu.map((item) => (
            <div key={item.id} className="rounded-2xl bg-white p-4 shadow">
              <div className="flex gap-4">
                <img
                  src={item.image_url || "https://via.placeholder.com/120"}
                  alt={item.name_en || item.name_th}
                  className="h-24 w-24 rounded-xl object-cover"
                />

                <div className="flex-1">
                  <h2 className="text-lg font-semibold text-gray-900">{item.name_th}</h2>
                  <p className="text-sm text-gray-500">{item.name_en}</p>

                  <div className="mt-3 flex items-center justify-between">
                    <div>
                      {item.is_promotion && item.promo_price ? (
                        <div className="flex items-center gap-2">
                          <span className="text-lg font-bold text-red-600">
                            ฿{item.promo_price}
                          </span>
                          <span className="text-sm text-gray-400 line-through">
                            ฿{item.price}
                          </span>
                        </div>
                      ) : (
                        <span className="text-lg font-bold text-gray-900">฿{item.price}</span>
                      )}
                    </div>

                    <button
                      onClick={() => addToCart(item)}
                      className="rounded-xl bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
                    >
                      Add
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="fixed bottom-0 left-0 right-0 border-t bg-white shadow-2xl">
        <div className="mx-auto max-w-3xl p-4">
          <h2 className="mb-3 text-lg font-bold text-gray-900">Cart</h2>

          {cart.length === 0 ? (
            <p className="text-sm text-gray-500">No items added yet</p>
          ) : (
            <>
              <div className="space-y-3">
                {cart.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between rounded-xl bg-gray-50 p-3"
                  >
                    <div>
                      <p className="font-medium text-gray-900">{item.name_th}</p>
                      <p className="text-sm text-gray-500">
                        ฿{item.price} x {item.qty} = ฿{item.price * item.qty}
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => decreaseQty(item.id)}
                        className="rounded-lg bg-gray-200 px-3 py-1"
                      >
                        -
                      </button>
                      <span className="min-w-6 text-center">{item.qty}</span>
                      <button
                        onClick={() => increaseQty(item.id)}
                        className="rounded-lg bg-gray-200 px-3 py-1"
                      >
                        +
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-4 flex items-center justify-between">
                <p className="text-lg font-bold text-gray-900">Total: ฿{totalAmount}</p>
                <button
                onClick={placeOrder}
                disabled={submitting}
                className="rounded-xl bg-green-600 px-5 py-3 text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:bg-green-300"
                >
                {submitting ? "Placing..." : "Place Order"}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </main>
  );
}