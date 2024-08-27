from factscore.lm import LM
import openai
import sys
import time
import os
import numpy as np
import logging

'''class OpenAIModel(LM):

    def __init__(self, model_name, cache_file=None, key_path="api.key"):
        self.model_name = model_name
        self.key_path = key_path
        self.temp = 0.7
        self.save_interval = 100
        super().__init__(cache_file)

    def load_model(self):
        # load api key
        key_path = self.key_path
        assert os.path.exists(key_path), f"Please place your OpenAI APT Key in {key_path}."
        with open(key_path, 'r') as f:
            api_key = f.readline()
        openai.api_key = api_key.strip()
        self.model = self.model_name

    def _generate(self, prompt, max_sequence_length=2048, max_output_length=128):
        if self.gpt3:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",  # 或者使用您想要的模型
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_output_length,
                    temperature=self.temp,
                    n=1,
                    stop=None
                )
                output = response.choices[0].message.content
                formatted_response = {
                    "choices": [{
                        "text": output,
                        "finish_reason": response.choices[0].finish_reason,
                        "index": 0,
                    }],
                    "usage": response.usage.to_dict() if hasattr(response, 'usage') else {},
                    "model": response.model,
                }
                return output, formatted_response
            except Exception as e:
                print(f"Error in _generate: {str(e)}")
                raise
        else:
            if self.add_n % self.save_interval == 0:
                self.save_cache()
            # return a tuple of string (generated text) and metadata (any format)
            # This should be about generating a response from the prompt, no matter what the application is
            if self.model_name == "ChatGPT":
                # Construct the prompt send to ChatGPT
                message = [{"role": "user", "content": prompt}]
                # Call API
                response = call_ChatGPT(message, temp=self.temp, max_len=max_sequence_length)
                # Get the output from the response
                output = response["choices"][0]["message"]["content"]
                return output, response
            elif self.model_name == "InstructGPT":
                # Call API
                response = call_GPT3(prompt, temp=self.temp)
                # Get the output from the response
                output = response["choices"][0]["text"]
                return output, response
            else:
                raise NotImplementedError()'''
class OpenAIModel(LM):

    def __init__(self, model_name, cache_file=None, key_path="api.key"):
        self.model_name = model_name
        self.key_path = key_path
        self.temp = 0.7
        self.save_interval = 100
        self.gpt3 = True if "gpt-3" in model_name.lower() else False
        super().__init__(cache_file)

    def load_model(self):
        # load api key
        key_path = self.key_path
        assert os.path.exists(key_path), f"Please place your OpenAI API Key in {key_path}."
        with open(key_path, 'r') as f:
            api_key = f.readline()
        openai.api_key = api_key.strip()
        self.model = self.model_name

    def _generate(self, prompt, max_sequence_length=2048, max_output_length=128):
        if self.add_n % self.save_interval == 0:
            self.save_cache()

        try:
            if self.gpt3 or self.model_name == "ChatGPT":
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_output_length,
                    temperature=self.temp,
                    n=1,
                    stop=None
                )
                output = response.choices[0].message.content
                formatted_response = {
                    "choices": [{
                        "text": output,
                        "finish_reason": response.choices[0].finish_reason,
                        "index": 0,
                    }],
                    "usage": response.usage.to_dict() if hasattr(response, 'usage') else {},
                    "model": response.model,
                }
            elif self.model_name == "InstructGPT":
                formatted_response = call_GPT3(prompt, temp=self.temp)
                output = formatted_response["choices"][0]["text"]
            else:
                raise NotImplementedError(f"Model {self.model_name} not implemented")

            return output, formatted_response
        except Exception as e:
            print(f"Error in _generate: {str(e)}")
            raise        

def call_ChatGPT(message, model_name="gpt-3.5-turbo", max_len=1024, temp=0.7, verbose=False):
    # call GPT-3 API until result is provided and then return it
    response = None
    received = False
    num_rate_errors = 0
    while not received:
        try:
            response = openai.ChatCompletion.create(model=model_name,
                                                    messages=message,
                                                    max_tokens=max_len,
                                                    temperature=temp)
            received = True
        except:
            # print(message)
            num_rate_errors += 1
            error = sys.exc_info()[0]
            if error == openai.error.InvalidRequestError:
                # something is wrong: e.g. prompt too long
                logging.critical(f"InvalidRequestError\nPrompt passed in:\n\n{message}\n\n")
                assert False
            
            logging.error("API error: %s (%d). Waiting %dsec" % (error, num_rate_errors, np.power(2, num_rate_errors)))
            time.sleep(np.power(2, num_rate_errors))
    return response

def call_GPT3(prompt, model_name="gpt-3.5-turbo", max_len=512, temp=0.7, num_log_probs=0, echo=False, verbose=False):
    # call GPT-3 API until result is provided and then return it
    response = None
    received = False
    num_rate_errors = 0
    while not received:
        try:
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_len,
                temperature=temp,
                n=1,
                stop=None
            )
            received = True
        except openai.error.InvalidRequestError as e:
            logging.critical(f"InvalidRequestError\nPrompt passed in:\n\n{prompt}\n\nError: {str(e)}\n\n")
            raise
        except Exception as e:
            error = type(e).__name__
            num_rate_errors += 1
            logging.error(f"API error: {error} ({num_rate_errors})")
            time.sleep(np.power(2, num_rate_errors))
    
    # 创建一个与旧API响应格式相似的字典
    formatted_response = {
        "choices": [{
            "text": response.choices[0].message.content,
            "finish_reason": response.choices[0].finish_reason,
            "index": 0,
        }],
        "usage": response.usage.to_dict() if hasattr(response, 'usage') else {},
        "model": response.model,
    }
    
    # 添加调试信息
    logging.debug(f"call_GPT3 returned: {formatted_response}")
    
    return formatted_response

# 替换原有的openai.Completion.create函数
openai.Completion.create = call_GPT3

'''def call_GPT3(prompt, model_name="gpt-3.5-turbo", max_len=512, temp=0.7, num_log_probs=0, echo=False, verbose=False):
    # call GPT-3 API until result is provided and then return it
    response = None
    received = False
    num_rate_errors = 0
    while not received:
        try:
            response = openai.ChatCompletion.create(model=model_name,
                                                prompt=prompt,
                                                max_tokens=max_len,
                                                temperature=temp,
                                                logprobs=num_log_probs,
                                                echo=echo)
            received = True
        except:
            error = sys.exc_info()[0]
            num_rate_errors += 1
            if error == openai.error.InvalidRequestError:
                # something is wrong: e.g. prompt too long
                logging.critical(f"InvalidRequestError\nPrompt passed in:\n\n{prompt}\n\n")
                assert False
            logging.error("API error: %s (%d)" % (error, num_rate_errors))
            time.sleep(np.power(2, num_rate_errors))
    return response'''

