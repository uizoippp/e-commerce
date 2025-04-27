import React from "react";
import Navbar from "./Navbar";
import Header from "./Header";
import Footer from "./Footer";

export default class FaceID extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            title: 'Face ID',
            ipcamera: '',
            previousImage: null,
            imageProcessed: null,
            message: '',
            sendImage: 500, // 100 mili giây gửi 1 ảnh
            isSending: true,
        };
        this.websocket = null;
        this.interval = null;
    }

    componentDidMount() {

        this.websocket = new WebSocket(`http://127.0.0.1:8000/ws/stream/${window.localStorage.getItem('id')}`);

        this.websocket.onopen = () => {
            console.log('Connected to websocket');
            this.startSendingImages();
        };

        this.websocket.onerror = (error) => {
            console.log("Websocket error:", error);
        };

        this.websocket.onclose = () => {
            console.log('websocket connection closed');
        };

        this.websocket.onmessage = (e) => {
            if (!e.data.startsWith('data:image/jpeg;base64')) {
                const data = JSON.parse(e.data);
                this.setState({ message: data.message })
            }
            else {
                this.setState({ imageProcessed: e.data });
            }
        };
    }

    componentWillUnmount = (e) => {
        if (this.websocket) {
            this.websocket.close();
        }
        if (this.interval) {
            clearInterval(this.interval);
        }
    }

    startSendingImages = () => {
        const imageElement = document.getElementById('camera');
        this.interval = setInterval(() => {
            if (imageElement && this.state.isSending) {
                this.sendImageToWebSocket(imageElement);
            }
        }, this.state.sendImage); // Gửi ảnh mỗi giây (1 lần/giây)

    }

    sendImageToWebSocket = (img) => {
        try {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);

            // Chuyển canvas thành base64
            const dataUrl = canvas.toDataURL("image/jpeg");

            // Kiểm tra xem ảnh hiện tại có thay đổi so với ảnh trước đó không
            if (this.state.previousImage !== dataUrl) {
                // Nếu ảnh khác so với lần trước, gửi nó qua WebSocket
                if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                    this.websocket.send(dataUrl);
                    console.log("Image sent to WebSocket");
                    this.setState({ previousImage: dataUrl }); // Cập nhật ảnh trước đó
                }
            } else {
                console.log("No new image to send.");
            }
        }
        catch (e) {
            console.log(e);
        }

    }

    handleIpcamera = (e) => {
        this.setState({ipcamera: `http://${e.target.value}:8080/video`});
    }

    handleSubmit = (e) => {
        e.preventDefault();
        this.setState({isSending: true});
    }

    submitImage = (e) => {
        this.websocket.send('submit');
        this.setState({ isSending: false })
    }

    render() {
        return (
            <>
                <Navbar />
                <Header title={this.state.title} />
                <div className="container-fluid py-5">
                    <div className="container">
                        <div className="row" style={{ justifyContent: 'center' }}>
                            <div className="col-lg-7">
                                <h1 className="mb-4">Nhập IP camera</h1>
                                <div className="contact-form bg-secondary" style={{ padding: "30px" }}>
                                    <form name="sentMessage" id="contactForm">
                                        <div className="control-group">
                                            <input type="text" className="form-control border-0 p-4" id="name" placeholder="IP camera"
                                                required="required" onChange={this.handleIpcamera} />
                                            <p className="help-block text-danger"></p>
                                        </div>
                                        {/* <div style={{ display: "flex", gridTemplateColumns: "repeat(2, 30%)", gap: "4em", justifyContent: "center" }}>
                                            <button onClick={this.handleSubmit} className="btn btn-primary py-3 px-4" type="submit" >Xác nhận</button>
                                        </div> */}
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                {this.state.isSending ? (<div className="container-fluid pt-5">
                    <div className="container">
                        <div className="text-center pb-2">
                            <h6 className="text-primary text-uppercase font-weight-bold">Camera</h6>
                            {this.state.message && (
                                <h1 className="mb-4">{this.state.message}</h1>
                            )}
                        </div>
                        <div className="row" style={{ justifyContent: 'center' }}>
                            <div className="col-lg-3 col-md-6" >
                                <div className="team card position-relative overflow-hidden border-0 mb-5">
                                    <img id="camera" className="card-img-top" crossOrigin="anonymous" src={this.state.ipcamera} alt="" style={{ width: '680px', height: '480px' }} />
                                    {/* {this.state.imageProcessed && (
                                        <img className="card-img-top" src={this.state.imageProcessed} alt="" style={{ width: '680px', height: '480px' }} />
                                    )} */}
                                    <button className="btn btn-primary py-3 px-4" style={{ margin: '5px auto' }} onClick={this.submitImage}>Gửi ảnh</button>

                                </div>
                            </div>
                        </div>
                    </div>
                </div >) : <h1>Tạo face ID thành công</h1>}
                <Footer />
            </>
        )
    }
}