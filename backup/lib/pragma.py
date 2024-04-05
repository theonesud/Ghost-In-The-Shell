from bs4 import BeautifulSoup

# from lib.driver import get_url


def reply(url):
    # source = get_url(url)
    # with open("scrapes/test_conv.html", "w") as f:
    #     f.write(source)
    with open("scrapes/test_conv.html", "r") as f:
        source = f.read()
    soup = BeautifulSoup(source, "html.parser")
    messages = soup.find_all("span", class_="message")
    formatted_messages = []
    for message in messages:
        role = (
            "merchant" if "message--merchant" in message.attrs["class"] else "customer"
        )
        actual_message_container = message.find("div", class_="actual-message")
        if actual_message_container:
            spans = actual_message_container.find("span").find_all("span")
            if len(spans):
                formatted_messages.append(
                    {
                        "role": role,
                        "contents": spans[0].text,
                    }
                )
    formatted_messages.reverse()
    for message in formatted_messages:
        print(f">>>>>>>{message['role'].capitalize()}:\n {message['contents']}\n\n")
