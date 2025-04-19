import Header from "../layout/Header";
import Footer from "../layout/Footer";

export default function NotFound404() {
    return (
        <>
            <Header />
            <section className="shop_section layout_padding">
                <div className="container">
                    <div className="heading_container heading_center">
                        <h2>
                            404 Not Found
                        </h2>
                    </div>
                </div>

            </section>
            <Footer />
        </>
    );
}