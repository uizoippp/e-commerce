import React from "react";
import Footer from "./Footer";
import Navbar from "./Navbar";
import Header from "./Header";

export default class FindFaceID extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            title: 'Login via Face ID',
            ipcamera: '',
            previousImage: null,
            imageProcessed: null,
            message: '',
            sendImage: 500, // mili giây gửi 1 ảnh
            isSending: true,
        }
    }
    openWebsocket() {
        this.websocket = new WebSocket(`http://127.0.0.1:8000/ws/check`);

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
            const data = e.data;
            if (!data.startsWith('data:image/jpeg;base64')) {
                const data = JSON.parse(e.data);
                if (data.type === 'submit') {
                    this.setState({
                        isSending: false,
                        message: data.message
                    })

                } if (data.type === 'user') {
                    window.localStorage.setItem('id', data.id);
                    window.localStorage.setItem('username', data.username);
                    window.localStorage.setItem('token', data.token);
                    window.location.href = '/';
                }
                else {
                    this.setState({ message: data.message })
                }
            }
            else {
                this.setState({ imageProcessed: data });
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
        this.setState({ ipcamera: `http://${e.target.value}:8080/video` });
    }

    submitIpcamera = (e) => {
        e.preventDefault();
        this.openWebsocket();
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
                                        <div style={{ display: "flex", gridTemplateColumns: "repeat(2, 30%)", gap: "4em", justifyContent: "center" }}>
                                            <button onClick={this.submitIpcamera} className="btn btn-primary py-3 px-4" type="submit" >Xác nhận</button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="container-fluid pt-5">
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
                                </div>
                            </div>
                        </div>
                    </div>
                </div >
                <Footer />
            </>
        )
    }
}